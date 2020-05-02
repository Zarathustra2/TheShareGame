"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""
from __future__ import annotations
import logging
import re


from datetime import timedelta
from decimal import Decimal

from django.db import models, transaction
from django.db.models import DecimalField, ExpressionWrapper, F, Sum, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.functional import cached_property
from django_countries.fields import CountryField
from rest_framework.reverse import reverse

from tsg.const import CENTRALBANK

logger = logging.getLogger(__name__)


class CompanyQuerySet(models.QuerySet):
    def delete(self):
        raise NotImplementedError("Cannot bulk delete companies")


class Company(models.Model):
    """
    Core-Model of this project.

    Users can have several companies, companies can buy other companies, create
    order, buy bonds and more.

    The goal is to get more money.

    Each company has a unique ISIN, but we do not use the ISIN as id, tho the id can be gotten from the isin
    """

    objects = CompanyQuerySet.as_manager()

    # null value allowed, since the CentralBank does not have a user account
    # Maybe it would be easier if we just create a user account for the
    # centralbank
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, null=True)

    name = models.CharField(max_length=25, null=False, unique=True)
    isin = models.CharField(max_length=10, unique=True)

    country = CountryField(default="US")

    cash = models.DecimalField(max_digits=25, decimal_places=2, default=0)

    shares = models.PositiveIntegerField(default=1000000)

    class Meta:
        db_table = "company"

    @classmethod
    def get_centralbank(cls) -> Company:
        """Returns the centralbank"""
        return cls.objects.get(name=CENTRALBANK)

    @classmethod
    def get_id_from_isin(cls, isin: str) -> int:
        """Returns the ID from the ISIN"""

        pattern = re.compile("^[A-Z]{2}[0-9]{6}$")
        if not pattern.match(isin):
            logger.info(f"{isin} did not match pattern")
            return -1

        # first 2 chars of the ISIN are the country-code, so we stripe them off
        return int(isin[2:])

    def id_from_isin(self) -> int:
        return self.get_id_from_isin(self.isin)

    @cached_property
    def amount_bonds(self) -> int:
        """Returns the amount of bonds currently in the depot of the company"""
        return self.bond_set.count()

    def enough_money(self, transaction_value) -> bool:
        """Returns True if the company has enough money for the transaction"""
        orders_value = (
            self.orders_by.add_value().filter(typ=Order.type_buy()).aggregate(s=Coalesce(Sum("value"), 0))["s"]
        )
        total = (self.cash - orders_value) - transaction_value
        if total < 0:
            logger.info(f"{self} does not have enough money, has: {total}, transaction_value: {transaction_value}")
        return total >= 0

    def bid(self) -> Order:
        """Bid is the price of the highest buy-orders"""

        buy_order = (
            self.orders_of.filter(typ=Order.type_buy())
            .values("price")
            .annotate(total_amount=Sum("amount"))
            .order_by("-price")
            .first()
        )

        return buy_order

    def ask(self) -> Order:
        """Ask is the price of the lowest sell-orders"""

        sell_order = (
            self.orders_of.filter(typ=Order.type_sell())
            .values("price")
            .annotate(total_amount=Sum("amount"))
            .order_by("price")
            .first()
        )

        return sell_order

    def get_absolute_url(self) -> str:
        """Returns the api url for a single company"""
        return reverse("core:company", kwargs={"isin": self.isin})

    def update_activity(self):
        Activity.objects.filter(company=self).update(updated=timezone.now())

    def save(self, *args, **kwargs):
        isin_update = kwargs.pop("isin_update", False)

        if isin_update:
            # when we update the isin
            # we can't use the same approach because otherwise we would change also the id value
            # so we only update the first two chars of the isin-string since they represent the country code
            # and this is the ONLY thing a user can update regarding the isin
            current = self.isin
            self.isin = f"{self.country}{current[2:]}"

        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):

        # When deleting a company, make sure they do not have a depot positions
        # or bonds
        if DepotPosition.objects.filter(depot_of=self).exists():
            raise ValueError("Company still has depot positions. Cannot be deleted!")

        if Bond.objects.filter(company=self).exists():
            raise ValueError("Company still has bonds. Cannot be deleted!")

        trades_count = Trade.objects.filter(Q(company=self) | Q(seller=self) | Q(buyer=self)).count()
        trades_history_count = TradeHistory.objects.filter(
            Q(company_name=self.name) | Q(seller_name=self.name) | Q(buyer_name=self.name)
        ).count()
        if trades_count != trades_history_count:
            raise ValueError("Trade history has not been implemented for all trades")

        return super().delete(using, keep_parents)

    def __str__(self):
        return self.name


class PrivateDepot(models.Model):
    """
    Each User has a single PrivateDepot.

    Users can buy shares with their PD, transfer money from their private depot
    in their company but not the other way around.

    Furthermore, if a private depot has bought shares of a company, then it cannot be
    seen in the shareholder structure whose private depot holds the shares.
    This makes the market more interesting especially when you want to take over other companies.

    On the other hand we need to have rules, so that users do not only use their private depot
    for buying shares.

    NOT IMPLEMENTED YET:
        => This will be implemented once everything else is running
    """

    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    cash = models.DecimalField(max_digits=25, decimal_places=2, default=0)

    class Meta:
        db_table = "private_depot"

    def __str__(self):
        return str(self.user)


class OrderQuerySet(models.QuerySet):
    """
    Custom QuerySet for the Order-Model to annotate data
    such as the value of an order
    """

    def add_value(self) -> models.QuerySet:
        """
        Annotates the value of an order.
        The value of an order is defined as the price multiplied by amount.

        This is especially useful when we want to query for the highest or
        lowest order.
        """
        return self.annotate(value=ExpressionWrapper(F("price") * F("amount"), output_field=DecimalField()))


class Order(models.Model):
    """
    Base-Model for creating an Order for a company.

    An order signals that a company wants to either buy or sell another company.
    If a company wants to sell shares, it must have the same amount in its depot.

    Furthermore, orders cannot be created if a company has not enough money.

    Orders can also be created with a private depot, which is not implemented
    yet.


    This is the base order model, other order types inherit from this model
    such as the DynamicOrder
    """

    # Tons of orders will be created and deleted, so we use
    # the BigAutoField instead of the Default AutoField
    id = models.BigAutoField(primary_key=True, editable=False)

    TYPES = [("Buy", "Buy"), ("Sell", "Sell")]

    objects = OrderQuerySet.as_manager()

    # the owner/ creator of the order
    order_by = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="orders_by")

    # The company, which the owner/creator wants to buy/sell
    order_of = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="orders_of")

    typ = models.CharField(choices=TYPES, max_length=4, null=False, blank=False, default=None)

    # user field when the private depot creates an order
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True)

    price = models.DecimalField(max_digits=25, decimal_places=2, default=0)
    amount = models.PositiveIntegerField()

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order"

    @classmethod
    def type_buy(cls) -> str:
        return "Buy"

    @classmethod
    def type_sell(cls) -> str:
        return "Sell"

    def __str__(self):
        return f"Order by:{self.order_by}, Order of: {self.order_of}, Amount: {self.amount}, Price: {self.price}"


class DynamicOrder(Order):
    """
    The price of a DynamicOrder falls/rises every tick while normal orders prices are static.

    This allows users to create orders where the price falls/rises by 2$ every
    tick.

    If a certain limit has been reached, the price of the order no longer falls/rises
    There should also be a cap, which checks if the owner of the order has
    enough money if the order has a rising price.
    """

    limit = models.DecimalField(max_digits=25, decimal_places=2, default=0)
    dynamic_value = models.DecimalField(max_digits=25, decimal_places=2, default=0)

    class Meta:
        db_table = "dynamic_order"


class Bond(models.Model):
    """
    Bonds can be bought by companies.

    Bonds have a fixed run time and companies get their money back inclusive interest rate


    Bonds create inflation in the market since they are given out by the system,
    and they will always exist. The limit for buying bonds is per company, so
    each company can have a maximum of 10 bonds. Companies can also as much
    money as they have in bonds.

    Tho, if they invest all of their money in bonds, they are unable to create
    orders.

    Furthermore, the more money the market invests in bonds the lower the rate
    of the bonds are. For more information see the InterestRate Model couple of
    lines down the file.
    """

    id = models.BigAutoField(primary_key=True, editable=False)

    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    value = models.DecimalField(max_digits=25, decimal_places=2, default=0)
    runtime = models.PositiveSmallIntegerField(default=1)

    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    day_time_issued = models.DateTimeField(auto_now_add=True)

    expires = models.DateTimeField(null=False, blank=False)

    class Meta:
        db_table = "bond"

    def calc_value(self) -> float:
        """Returns the payout of the bond"""
        value = self.value * Decimal((self.rate / 100) + 1) ** self.runtime
        return round(value, 2)

    def __str__(self):
        return f"{self.company}: {self.value}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.expires is None:
            # if expires is null than day_time_issued is also null
            self.day_time_issued = timezone.now()
            self.expires = self.day_time_issued + timedelta(days=self.runtime)

        super().save(force_insert, force_update, using, update_fields)


class DepotPositionQuerySet(models.QuerySet):
    def add_value(self) -> models.QuerySet:
        """
        Adds the value of a position to the queryset.

        A value of a position is defined by the current share_price of the
        position multiplied by the amount of shares in the depot of the owner.
        """
        # TODO: Is it possible to log a warning if the query did not use select_related?
        return self.annotate(
            value=ExpressionWrapper(F("amount") * F("company__keyfigures__share_price"), output_field=DecimalField())
        )

    def add_percentage(self) -> models.QuerySet:
        """
        Adds the percentage of a position to queryset.

        Percentage signals how many of a company's shares a company holds.

        If company A has a total of 100,000 Shares and company B holds 50,000
        Shares in his depot, then he has a percentage of 50% of the shares.
        """
        return self.annotate(
            percentage=ExpressionWrapper(F("amount") * 100 / F("company__shares"), output_field=DecimalField())
        )


class DepotPosition(models.Model):
    """
    Represents a position in the Depot of a Company or PrivateDepot
    """

    objects = DepotPositionQuerySet.as_manager()

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="in_depots")

    depot_of = models.ForeignKey(Company, on_delete=models.CASCADE)

    amount = models.PositiveIntegerField(default=0)

    price_bought = models.DecimalField(max_digits=25, decimal_places=2, default=0)

    created = models.DateTimeField(auto_now_add=True)

    private_depot = models.BooleanField(default=False)

    class Meta:
        # Each company should have another company only once in his depot.
        # Company A should not be able to have two positions of Company B in his depot.
        unique_together = ["company", "depot_of", "private_depot"]
        db_table = "depot_position"

    def __str__(self):
        return f"Depot: {self.depot_of}, Share: {self.company}"


class InterestRate(models.Model):
    """
    InterestRate for the current Tick.

    Rates influence the bonds and how much money a company gets back from investing in a bond.

    Basically, the more companies invest in bonds the less the rate and if only
    a few companies invest in bonds, then the rate will be higher.


    For the actual calculation see periodic_tasks/rates.py
    """

    rate = models.DecimalField(max_digits=5, decimal_places=2, default=2)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "interest_rate"

    @classmethod
    def get_latest_rate(cls) -> Decimal:
        """Returns the latest rate"""
        # TODO: Cache until next hour
        return cls.objects.latest("id").rate

    @classmethod
    def calc_rate(cls, value) -> Decimal:
        """
        Calculates the rate for a value.
        The higher the value the less the interest rate will be.
        """
        rate = cls.get_latest_rate()
        if value < 100000:
            return rate
        return rate * Decimal(100 * 0.1) * value ** Decimal(-0.2)

    def __str__(self):
        return f"{self.day_time}: {self.rate}"


class TradeQuerySet(models.QuerySet):
    def add_value(self):
        return self.annotate(value=ExpressionWrapper(F("price") * F("amount"), output_field=DecimalField()))


class Trade(models.Model):
    """
    Model to store a Trade (=seller & buyer of a share)

    TODO: We should look forward to implementing multiple tables for this model.
        After days have passed move all the data to another table.
        So for each day we know in which table to check for the data:
        See here for more information: https://stackoverflow.com/questions/5036357/single-django-model-multiple-tables
    """

    id = models.BigAutoField(primary_key=True, editable=False)

    objects = TradeQuerySet.as_manager()

    # Whenever a company gets deleted we want to keep the trade.
    # Hence we allow null values. If a company gets deleted the name of the comapny
    # gets stored in the TradeHistory model.
    buyer = models.ForeignKey(Company, related_name="trades_buyer", on_delete=models.SET_NULL, null=True)
    seller = models.ForeignKey(Company, related_name="trades_seller", on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey(Company, related_name="trades_of", on_delete=models.SET_NULL, null=True)

    price = models.DecimalField(max_digits=40, decimal_places=2, default=0)
    amount = models.PositiveIntegerField(default=1)

    # the price the buyer paid to buy the shares initially
    # comparing price_bought with price let's us quickly determine
    # if the buyer made profit or not
    price_bought = models.DecimalField(max_digits=40, decimal_places=2, default=1)

    created = models.DateTimeField(auto_now_add=True)

    # Users can also trade with their private depot
    # there is no need to add a user field, since every company
    # belongs to exactly one user, so we can access them over the company
    # TODO: That is not true actually. If a company gets deleted or overtaken
    # this may be a problem
    # save user field as well
    buyer_pd = models.BooleanField(default=False)
    seller_pd = models.BooleanField(default=False)

    class Meta:
        db_table = "trade"

    def __str__(self):
        return f"{self.company}: Buyer: {self.buyer}, Seller: {self.seller}"

    def get_value(self) -> Decimal:
        return self.price * self.amount

    @classmethod
    def create_trade_histories(cls, company: Company):
        """
        Filters all trades for which the given company is involved and creates
        trades history models.

        This method is called when the given company gets deleted, and we want to
        save the trades where the company has been involded.

        """
        qs = cls.objects.filter(Q(company=company) | Q(seller=company) | Q(buyer=company))

        trade_histories = list()

        with transaction.atomic():
            for trade in qs:
                # TODO: Move into qs query.
                if TradeHistory.objects.filter(trade_id=trade.id).exists():
                    continue
                trade_histories.append(
                    TradeHistory(
                        trade=trade,
                        company_name=trade.company.name,
                        seller_name=trade.seller.name,
                        buyer_name=trade.buyer.name,
                    )
                )
                if len(trade_histories) > 500:
                    TradeHistory.objects.bulk_create(trade_histories)
                    trade_histories = list()

            if len(trade_histories) > 0:
                TradeHistory.objects.bulk_create(trade_histories)


class TradeHistory(models.Model):
    """
    Stores the plain names of the Buyer, Seller, Company when one of them
    gets deleted.

    This allows use to retrieve the names of the company involved in the trade.
    """

    trade = models.OneToOneField(Trade, on_delete=models.CASCADE)

    buyer_name = models.CharField(max_length=50, null=True, blank=True)
    seller_name = models.CharField(max_length=50, null=True, blank=True)
    company_name = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "trade_history"


class Activity(models.Model):
    """
    Model to store the time of the last activity of a company

    Following actions count as activity:
        1. Create an order
        2. Buy a bond
        3. Take over another company
        4. Matching of orders

    If a company is not active over a certain time span, then the liquidation
    of the company starts automatically.

    TODO: Add Liquidation model and periodic_task
    """

    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "activity"

    def __str__(self):
        return f"{self.company} last activity: {self.updated}"


class StatementOfAccount(models.Model):
    """
    Model to store all Transactions of a Company

    Transactions are for instance:
        - buying/selling shares
        - buying bonds & getting paid back
    """

    TYPES = [("Order", "Order"), ("Bond", "Bond")]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    typ = models.CharField(choices=TYPES, max_length=25, null=False)

    value = models.DecimalField(max_digits=40, decimal_places=2)

    amount = models.PositiveIntegerField(null=True)

    received = models.BooleanField()

    created = models.DateTimeField(auto_now_add=True)

    trade = models.ForeignKey(Trade, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "statement_of_account"

    def __str__(self):
        return f"{self.company} type: {self.typ}, value: {self.value}"

    def clean(self):
        super().clean()
        if self.is_order():
            logger.info(self)
            if self.trade is None:
                raise ValueError(f"Cannot create {self.__class__} without trade object!")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.clean()
        super().save(force_insert, force_update, using, update_fields)

    def is_order(self) -> bool:
        return self.typ == "Order"
