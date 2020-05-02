"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import logging
from decimal import Decimal

from django.db.models import F
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import DateTimeField

from core.models import Bond, Company, DepotPosition, InterestRate, Order, StatementOfAccount, Trade
from periodic_tasks.orders import check_orders_single_company
from stats.serializers import KeyFiguresSerializer
from tsg.const import DATETIME_FORMAT, START_CASH
from users.serializers import UserSerializer

logger = logging.getLogger(__name__)


class CompanyKeyFiguresLogoSerializer(serializers.ModelSerializer):
    """
    CompanySerializer, which also serializes key figures of the company and his logo.
    """

    user = UserSerializer()
    key_figures = KeyFiguresSerializer(source="keyfigures")
    logo = serializers.ImageField(source="user.profile.company_logo", allow_null=True, default=None)

    class Meta:
        model = Company
        fields = ("isin", "name", "country", "cash", "shares", "user", "key_figures", "id", "logo")
        read_only_fields = fields


class CompanySerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Company
        fields = ("isin", "name", "country", "cash", "shares", "user", "id")
        read_only_fields = fields


class CompanyUrlSerializer(serializers.ModelSerializer):
    """
    Serializes the name, user_id & isin of a Company.
    This allows the frontend to build an url to the company.
    """

    class Meta:
        model = Company
        fields = ("name", "user_id", "isin", "id")
        read_only_fields = fields


class CompanySidebarSerializer(serializers.ModelSerializer):

    share_price = serializers.DecimalField(source="keyfigures.share_price", max_digits=40, decimal_places=2)

    class Meta:
        model = Company
        fields = ("name", "isin", "id", "share_price")
        read_only_fields = fields


class FirstCompanyCreationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating the first company of a user

    When users register they can found a company and choose the name, the country and
    the amount of shares of the company.
    """

    class Meta:
        model = Company
        fields = ("name", "country", "shares", "isin", "user_id")
        read_only_fields = ("isin", "user_id")

    def create(self, validated_data):

        user = self.context["request"].user

        name = validated_data["name"]
        country = validated_data["country"]
        shares = validated_data["shares"]

        with transaction.atomic():
            company = Company.objects.create(user=user, name=name, country=country, shares=shares, cash=START_CASH)

        return company

    def validate(self, attrs):
        user = self.context["request"].user
        if Company.objects.filter(user_id=user.id).exists():
            raise serializers.ValidationError("You already have a Company!")
        return attrs

    def validate_shares(self, value):

        # On creation the amount of shares should be between 1_000 and 1_000_000
        # During the game it is though possible to have more than 1_000_000 shares/ less than 1_000 shares through
        # capital raises / reductions.
        if value > 1_000_000 or value < 1_000:
            raise serializers.ValidationError("Shares need to be between 1,000 and 1,000,000")
        return value


class BondSerializer(serializers.ModelSerializer):
    """
    Serializes a bond.
    """

    company_isin = serializers.CharField(write_only=True, max_length=25)
    expires = DateTimeField(format=DATETIME_FORMAT, read_only=True)

    class Meta:
        model = Bond
        fields = ("id", "value", "rate", "runtime", "expires", "company_isin")
        read_only_fields = ("id", "company", "expires", "rate")

    def validate(self, data):
        company_id = Company.get_id_from_isin(data["company_isin"])
        c = Company.objects.get(id=company_id)

        value = data["value"]

        if not c.enough_money(value):
            raise serializers.ValidationError({"value": f"You do not have enough money to buy a {value} bond"})
        return data

    def create(self, validated_data):
        company_isin = validated_data.get("company_isin")

        value = validated_data.get("value")
        runtime = validated_data.get("runtime")

        rate = InterestRate.calc_rate(value)
        company_id = Company.get_id_from_isin(company_isin)
        with transaction.atomic():

            # TODO: I think this can be replaced by simply writing:
            # c.cash = c.cash - value
            # as this inside in a transaction atomic block but I am not 100% sure
            # Need to check the docs
            Company.objects.filter(id=company_id).update(cash=F("cash") - value)
            bond = Bond.objects.create(company_id=company_id, value=value, rate=rate, runtime=runtime)

        return bond

    def validate_runtime(self, value):
        if value < 0 or value > 3:
            raise serializers.ValidationError(_("Runtime to long/short"))
        return value

    def validate_value(self, value):
        if value < 0:
            raise serializers.ValidationError(_("Value cannot be negative"))
        return value


class OrderSerializer(serializers.ModelSerializer):

    created = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)
    value = serializers.DecimalField(max_digits=40, decimal_places=2, read_only=True)
    order_of = CompanyUrlSerializer(read_only=True)
    order_by = CompanyUrlSerializer(read_only=True)

    order_of_isin = serializers.CharField(write_only=True, max_length=25)

    class Meta:
        model = Order
        fields = (
            "order_by",
            "order_of",
            "typ",
            "price",
            "amount",
            # read only
            "created",
            "value",
            "id",
            # write only
            "order_of_isin",
        )
        read_only_fields = ("created", "value", "id")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = None
        request = self.context["request"]
        user = request.user if request is not None else None
        if user is not None and not user.is_anonymous:
            self.company = user.company

    def to_representation(self, instance):
        data = super().to_representation(instance)

        user = self.context["request"].user

        # Other users should not be allowed to see who
        # created the order
        # Maybe create a different serializer for the page
        # where the user sees with which company he created which order
        if data["order_by"].get("user_id", -1) != user:
            del data["order_by"]

        return data

    def validate_price(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError(_("Price cannot be equal or less than 0"))
        return value

    def validate_amount(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError(_("Amount cannot be equal or less than 0"))
        return value

    def validate_order_of_isin(self, value: str) -> str:
        """
        Validate that the order_of isin is valid. It must be an existing company and not the same as the
        buying company.
        """
        if value == self.company.isin:
            raise serializers.ValidationError(_("You cannot create an order for your own company!"))

        if not Company.objects.filter(id=Company.get_id_from_isin(value)).exists():
            raise serializers.ValidationError(_("A company with the given isin does not exist"))

        if Company.get_centralbank().isin == value:
            raise serializers.ValidationError(_("You cannot place an order on the Centralbank"))

        return value

    def validate_enough_money(self, value) -> None:
        """
        Validate that the buying company has enough money
        """
        company = self.company

        if company.enough_money(transaction_value=value) is False:
            raise serializers.ValidationError(_("You do not have enough Cash"))

    def validate_sell_order(self, amount: int, order_of_id: int) -> None:
        """
        Validate that the selling company has the amount of shares in his depot
        """
        try:
            d = DepotPosition.objects.get(depot_of=self.company, company_id=order_of_id)
        except DepotPosition.DoesNotExist:
            logger.exception(f"{self.company} does not have {order_of_id} in his depot")
            raise serializers.ValidationError({"order_of_isin": "You do not have this company in your depot"})

        if d.amount < amount:
            raise serializers.ValidationError(
                {"amount": f"You only have {d.amount} shares in your depot but want to sell {amount}!"}
            )

    def validate(self, data):
        order_by_isin = self.company.isin
        order_of_isin = data.get("order_of_isin")

        self.validate_order_of_isin(order_of_isin)

        order_by_id = Company.get_id_from_isin(order_by_isin)
        order_of_id = Company.get_id_from_isin(order_of_isin)

        price = data.get("price")
        amount = data.get("amount")

        typ = data.get("typ")
        if typ == Order.type_sell():
            self.validate_sell_order(amount, order_of_id)

        value = price * amount
        self.validate_enough_money(value=value)

        if Order.objects.filter(order_by_id=order_by_id).count() > 100:
            raise serializers.ValidationError("You already have more than 100 orders!")

        return data

    def create(self, validated_data) -> Order:
        order_by_isin = self.company.isin
        order_of_isin = validated_data.get("order_of_isin")

        order_by_id = Company.get_id_from_isin(order_by_isin)
        order_of_id = Company.get_id_from_isin(order_of_isin)

        price = validated_data.get("price")
        amount = validated_data.get("amount")
        typ = validated_data.get("typ")

        order = Order.objects.create(
            order_by_id=order_by_id, order_of_id=order_of_id, amount=amount, price=price, typ=typ
        )

        check_orders_single_company.delay(order_of_id)

        return order


class InterestRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestRate
        fields = ("rate", "created", "id")
        read_only_fields = fields


class ShareholderSerializer(serializers.ModelSerializer):
    depot_of = CompanyUrlSerializer()
    created = serializers.DateTimeField(format=DATETIME_FORMAT)

    class Meta:
        model = DepotPosition
        fields = ("depot_of", "amount", "price_bought", "created", "private_depot", "id")
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if data["private_depot"]:
            del data["depot_of"]

        return data


class DepotPositionNameValueSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="company.name")
    value = serializers.DecimalField(max_digits=40, decimal_places=2)

    class Meta:
        model = DepotPosition
        fields = ("name", "value")
        read_only_fields = fields


class DepotPositionSerializer(serializers.ModelSerializer):
    company = CompanyUrlSerializer()
    created = serializers.DateTimeField(format=DATETIME_FORMAT)
    share_price = serializers.DecimalField(source="company.keyfigures.share_price", max_digits=40, decimal_places=2)

    class Meta:
        model = DepotPosition
        fields = ("company", "amount", "price_bought", "created", "id", "share_price")
        read_only_fields = fields


class StatementOfAccountSerializer(serializers.ModelSerializer):
    company = CompanyUrlSerializer()
    created = serializers.DateTimeField(format=DATETIME_FORMAT)

    class Meta:
        model = StatementOfAccount
        fields = ("company", "typ", "value", "received", "created", "id", "amount")
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.is_order():
            trade = instance.trade
            if trade:
                trade.value = trade.get_value()
                data["trade"] = TradeSerializer(instance=trade, context={"request": self.context["request"]}).data

        return data


class TradeSerializer(serializers.ModelSerializer):
    buyer = CompanyUrlSerializer()
    seller = CompanyUrlSerializer()
    company = CompanyUrlSerializer()
    value = serializers.DecimalField(max_digits=40, decimal_places=2)
    created = serializers.DateTimeField(format=DATETIME_FORMAT)

    class Meta:
        model = Trade
        fields = (
            "buyer",
            "seller",
            "company",
            "price",
            "amount",
            "price_bought",
            "created",
            "buyer_pd",
            "seller_pd",
            "value",
            "id",
        )
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context["request"].user
        anonymous = user.is_anonymous

        # We do not want to pass the data about users
        # who bought with their private depot
        # Hence, we delete the buyer and seller field
        if data["buyer_pd"]:
            if anonymous or user.id != data["buyer"]["user_id"]:
                del data["buyer"]

        if data["seller_pd"]:
            if anonymous or user.id != data["seller"]["user_id"]:
                del data["seller"]

        history = dict()

        # if it has a tradehistory instance
        # then one of the companies got deleted
        if hasattr(instance, "tradehistory"):
            h = instance.tradehistory

            # we could discuss if we make the private depots public if the
            # company gets deleted
            if not data["buyer_pd"]:
                history["buyer_name"] = h.buyer_name
            if not data["seller_pd"]:
                history["seller_name"] = h.seller_name
            history["company_name"] = h.company_name

        data["history"] = history

        return data
