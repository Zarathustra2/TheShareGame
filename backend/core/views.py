"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import logging

from django.db.models import DecimalField, OuterRef, Subquery, Sum, Count, Q
from django.db.models.functions import Coalesce
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from common.pagination import StandardResultsSetPagination
from common.views import BaseListAPIServerSide
from core.models import Bond, Company, DepotPosition, InterestRate, Order, StatementOfAccount, Trade
from core.serializers import (
    BondSerializer,
    CompanyKeyFiguresLogoSerializer,
    CompanySerializer,
    CompanyUrlSerializer,
    DepotPositionSerializer,
    InterestRateSerializer,
    OrderSerializer,
    ShareholderSerializer,
    StatementOfAccountSerializer,
    TradeSerializer,
    FirstCompanyCreationSerializer,
    DepotPositionNameValueSerializer,
    CompanySidebarSerializer,
)
from tsg.const import MAXIMUM_BONDS

logger = logging.getLogger(__name__)


class CompanyJsonRenderer(JSONRenderer):
    """
    Custom Renderer used by multiple views such as depot, statement of account, trades and more
    to add a company field at the root of the json document.
    This allows the frontend to get also the name since they only request with the isin of a company
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        kwargs = renderer_context.get("kwargs")
        isin = kwargs.get("isin")
        if isin and isinstance(data, dict):
            try:
                company = Company.objects.only("name").get(id=Company.get_id_from_isin(isin))
            except Company.DoesNotExist:
                logger.info(f"Company with isin {isin} does not exist!")
                raise Http404
            data["company_name"] = company.name
        return super().render(data, accepted_media_type, renderer_context)


class CompanyViewMixin(APIView):
    def get_id(self):
        isin = self.kwargs.get("isin")
        return Company.get_id_from_isin(isin)


class CompanyRetrieveView(RetrieveAPIView):
    """
    Returns a Company by isin
    """

    serializer_class = CompanyKeyFiguresLogoSerializer

    def get_object(self):
        return get_object_or_404(Company.objects.select_related("keyfigures"), isin=self.kwargs["isin"])


class CompanyListCreateView(BaseListAPIServerSide, ListCreateAPIView):
    """
    Returns all Companies
    """

    queryset = Company.objects.all().select_related("user")
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request is not None and self.request.method == "POST":
            return FirstCompanyCreationSerializer
        return CompanySerializer

    def get_fields_sortable(self) -> [str]:
        fields = super().get_fields_sortable()
        fields += ["isin", "user", "name", "shares"]
        return fields


class BondListCreateView(BaseListAPIServerSide, ListCreateAPIView):
    """
    Returns either the bonds of a company or
    creates a new one.
    """

    serializer_class = BondSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = StandardResultsSetPagination
    queryset = Bond.objects.all()

    def get_filter_kwargs(self):
        return {"company__isin": self.kwargs["isin"]}

    def create(self, request, *args, **kwargs):

        # TODO: Move to Serializer

        amount = request.data.get("amount")
        runtime = request.data.get("runtime")
        value = request.data.get("value")

        if not amount:
            return Response("Amount empty", status=status.HTTP_400_BAD_REQUEST)

        if not value:
            return Response("Value empty", status=status.HTTP_400_BAD_REQUEST)

        if not runtime:
            return Response("Runtime empty", status=status.HTTP_400_BAD_REQUEST)

        amount = int(amount)
        value = int(value)
        runtime = int(runtime)

        isin = self.kwargs.get("isin")

        # TODO: Set parameter in settings
        # Check the amount of bonds
        # Place it as high as possible so users cannot make requests which would cause
        # long calculating loops in the next lines
        if int(amount) > 10:
            logger.info(f"Amount was greater than 10: {amount}. Request by {self.request.user}")
            return Response("Amount greater than 10", status=status.HTTP_400_BAD_REQUEST)

        company = get_object_or_404(Company, isin=isin, user=self.request.user)

        self.validate_amount(amount, company)

        self.validate_enough_money(company, value=value * amount)

        bonds = []
        for _ in range(amount):
            bonds.append({"value": value, "runtime": runtime, "company_isin": isin})

        serializer = self.get_serializer(data=bonds, many=True)

        if serializer.is_valid():
            serializer.save()
            headers = self.get_success_headers(serializer.data)

            # Update last activity
            company.update_activity()

            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @classmethod
    def validate_amount(cls, amount, company):

        remaining = MAXIMUM_BONDS - company.amount_bonds
        if amount > remaining:
            logger.info(f"Bond amount is greater than remaining: {amount} > {remaining}")
            raise serializers.ValidationError({"amount": _("This is above the bond limit of %s" % MAXIMUM_BONDS)})

    @classmethod
    def validate_enough_money(cls, company, value):

        if not company.enough_money(transaction_value=value):
            raise serializers.ValidationError(_("You don't have enough money!"))


class OrderListCreateAPIView(BaseListAPIServerSide, ListCreateAPIView):
    """
    get:
    Returns all orders ordered by date_time

    post:
    Create a new order

    TODO: Add delete method
    """

    serializer_class = OrderSerializer
    queryset = Order.objects.add_value().select_related("order_of", "order_by").all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = StandardResultsSetPagination

    def get_fields_sortable(self) -> [str]:
        fields = super().get_fields_sortable()
        fields += ["value", "typ", "price", "amount", "created", "order_of"]
        return fields


class UserOrderListAPIView(BaseListAPIServerSide, ListAPIView):
    """
    Returns all orders of the user
    """

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
    queryset = Order.objects.add_value().select_related("order_of", "order_by").all()

    def get_filter_kwargs(self):
        return {"order_by__user": self.request.user}

    def get_fields_sortable(self) -> [str]:
        fields = super().get_fields_sortable()
        fields += ["value", "typ", "price", "amount", "created", "order_of"]
        return fields


class ActiveCompanyRetrieveView(RetrieveAPIView):
    """
    Returns a company of the user

    TODO: Router with companies action route
    """

    serializer_class = CompanyUrlSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        user = self.request.user
        obj = Company.objects.filter(user=user).first()

        if obj is None:
            logger.info(f"{user} does not have a company")
            raise Http404

        return obj


class ShareholdersListView(CompanyViewMixin, ListAPIView):
    """
    Returns the Shareholder of a company by isin
    """

    serializer_class = ShareholderSerializer

    def get_queryset(self):
        id_ = self.get_id()
        return DepotPosition.objects.filter(company_id=id_).select_related("depot_of").order_by("-amount")


class InterestRateViewSet(viewsets.ViewSet):
    """
    ViewSet for retrieving either a list of interest rates
    or the most recent one
    """

    def list(self, request):
        """
        Returns the last 72 interest rates, which gets used by the front end
        for the rates-chart
        """
        queryset = InterestRate.objects.order_by("-created")[:72][::-1]
        serializer = InterestRateSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def latest(self, request):
        """
        Returns the latest interest-rate
        """

        obj = InterestRate.objects.latest("id")
        serializer = InterestRateSerializer(obj)
        return Response(serializer.data)


class DepotPositionViewSet(BaseListAPIServerSide, CompanyViewMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for the depot of a company

    list: returns the paginated depot

    slim: returns all positions in the depot with the name of the company, and the value
    """

    pagination_class = StandardResultsSetPagination
    renderer_classes = (CompanyJsonRenderer,)

    @action(detail=False, methods=["get"])
    def slim(self, request, isin=None):
        id_ = self.get_id()
        qs = DepotPosition.objects.add_value().select_related("company").filter(depot_of_id=id_, private_depot=False)
        serializer = self.get_serializer_class()(qs, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.path.endswith("slim/"):
            return DepotPositionNameValueSerializer
        return DepotPositionSerializer

    def get_order(self) -> str:
        return "-amount"

    def get_queryset_list(self):
        id_ = self.get_id()
        qs = (
            DepotPosition.objects.select_related("company")
            .filter(depot_of_id=id_, private_depot=False)
            .select_related("company__keyfigures")
        )
        return qs


class LiquidityRetrieveView(APIView):
    """
    Returns the Data for the Liquidity-Chart
    """

    def get(self, request, *args, **kwargs):
        #     The Liquidity states where the company has invested its money
        #     and how much he holds in reverse.
        #
        #     Currently, there are 3 multi-options:
        #         - Company has cash
        #         - Company has bonds
        #         - Company has invested in shares/stocks
        #
        #     Hence, we need to retrieve data from 3 different tables.
        isin = self.kwargs["isin"]
        company = (
            Company.objects.only("cash", "isin")
            .filter(id=Company.get_id_from_isin(isin))
            .annotate(
                bond_value=Coalesce(
                    Subquery(
                        Bond.objects.filter(company_id=OuterRef("id"))
                        .values("company_id")
                        .annotate(s=Sum("value"))
                        .values("s")[:1],
                        output_field=DecimalField(),
                    ),
                    0,
                ),
                depot_value=Coalesce(
                    Subquery(
                        DepotPosition.objects.add_value()
                        .filter(depot_of_id=OuterRef("id"))
                        .values("depot_of_id")
                        .annotate(s=Sum("value"))
                        .values("s")[:1],
                        output_field=DecimalField(),
                    ),
                    0,
                ),
            )
            .values("cash", "bond_value", "depot_value")
        )

        company = company.first()

        if not company:
            raise Http404

        data = {"cash": company["cash"], "bonds": company["bond_value"], "depot_value": company["depot_value"]}

        return Response(data=data)


class StatementOfAccountListView(BaseListAPIServerSide, CompanyViewMixin, ListAPIView):
    """
    View for retrieving the statement of account entries of a company
    given by isin.
    """

    serializer_class = StatementOfAccountSerializer
    queryset = StatementOfAccount.objects.select_related("trade").all()
    pagination_class = StandardResultsSetPagination

    def get_filter_kwargs(self):
        return {"company_id": self.get_id()}

    def get_fields_sortable(self) -> [str]:
        fields = super().get_fields_sortable()
        fields += ["value", "typ", "received", "amount", "created"]
        return fields


class OrderCompanyViewSet(BaseListAPIServerSide, CompanyViewMixin, CreateAPIView, ListAPIView):
    """
    get:
    Returns all orders of a company

    post:
    Create a new order for the given company

    delete:
    Delete an order given by an id of a company
    """

    serializer_class = OrderSerializer
    pagination_class = StandardResultsSetPagination
    queryset = Order.objects.all()

    def get_queryset(self):
        return super().get_queryset().add_value()

    def get_filter_kwargs(self):
        id_ = self.get_id()
        return {"order_of_id": id_}

    def delete(self, request, *args, **kwargs):
        id_ = self.get_id()
        user = self.request.user

        # I don't like this. Make order_id a parameter in the actual url.
        # TODO
        order_id = request.data.get("order_id")

        if user.is_anonymous:
            raise PermissionDenied

        # TODO: PermissionClass?
        # Might not be necessary because we query with the user
        # but may be cleaner
        Order.objects.filter(id=order_id, order_by_id=id_, order_by__user=user).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_fields_sortable(self) -> [str]:
        fields = super().get_fields_sortable()
        fields += ["value", "typ", "price", "amount", "created", "order_of"]
        return fields


class TradeListView(BaseListAPIServerSide, ListAPIView):
    """
    Returns all trades
    """

    serializer_class = TradeSerializer
    pagination_class = StandardResultsSetPagination
    queryset = Trade.objects.add_value().select_related("buyer", "seller", "company", "tradehistory").all()

    def get_fields_sortable(self) -> [str]:
        fields = super().get_fields_sortable()
        fields += ["value", "price", "amount", "buyer", "seller", "created"]
        return fields


class TradeCompanyListView(CompanyViewMixin, TradeListView):
    """
    Returns the trades of a company
    """

    renderer_classes = (CompanyJsonRenderer,)

    def get_filter_kwargs(self):
        id_ = self.get_id()
        return {"seller_id": id_, "seller_pd": False}


class BuyerSellerListView(TradeCompanyListView):
    """
    Returns the Buyer/Sellers of a company
    """

    def get_filter_kwargs(self):
        id_ = self.get_id()
        return {"company_id": id_}


class SidebarInfoRetrieveView(RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        data = dict()

        # TODO: Cache queries
        companies = Company.objects.select_related("keyfigures").order_by("-id")[:5]
        bond_rate = InterestRate.get_latest_rate()
        companies_count = Company.objects.count()

        orders = Order.objects.aggregate(
            sell_count=Count("id", filter=Q(typ=Order.type_sell())),
            buy_count=Count("id", filter=Q(typ=Order.type_buy())),
        )
        sell_orders_count = orders.get("sell_count")
        buy_orders_count = orders.get("buy_count")

        serializer = CompanySidebarSerializer(companies, many=True)

        data["companies"] = serializer.data
        data["bond_rate"] = bond_rate
        data["companies_count"] = companies_count
        data["buy_orders_count"] = buy_orders_count
        data["sell_orders_count"] = sell_orders_count

        return Response(data=data)


class LiquidityOverviewView(RetrieveAPIView):
    """
    Returns the liquidity overview for the authenticated user.

    The data returned is:
        - cash
        - value of all buy orders by the current user
        - bond values
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user_id = request.user.id

        company = (
            Company.objects.only("cash", "user_id")
            .filter(user_id=user_id)
            .annotate(
                bond_value=Coalesce(
                    Subquery(
                        Bond.objects.filter(company_id=OuterRef("id"))
                        .values("company_id")
                        .annotate(s=Sum("value"))
                        .values("s")[:1],
                        output_field=DecimalField(),
                    ),
                    0,
                ),
                buy_orders=Coalesce(
                    Subquery(
                        Order.objects.add_value()
                        .filter(order_by_id=OuterRef("id"), typ=Order.type_buy())
                        .values("order_by_id")
                        .annotate(s=Sum("value"))
                        .values("s")[:1],
                        output_field=DecimalField(),
                    ),
                    0,
                ),
            )
            .values("cash", "bond_value", "buy_orders")
        )

        company = company.first()

        if not company:
            raise Http404

        data = {"cash": company["cash"], "bonds": company["bond_value"], "buy_orders": company["buy_orders"]}

        return Response(data=data)
