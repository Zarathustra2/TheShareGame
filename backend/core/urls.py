"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from django.urls import path
from rest_framework import routers

from core import views

app_name = "core"

router = routers.SimpleRouter()
router.register(r"rates", views.InterestRateViewSet, "rate")
router.register(r"companies/(?P<isin>[-\w]+)/depot", views.DepotPositionViewSet, "depot")

urlpatterns = [
    path("companies/", views.CompanyListCreateView.as_view(), name="companies"),
    path("companies/get/active/", views.ActiveCompanyRetrieveView.as_view(), name="active_company"),
    path("companies/liquidity/", views.LiquidityOverviewView.as_view(), name="liquidity_overiew"),
    path("companies/<slug:isin>/", views.CompanyRetrieveView.as_view(), name="company"),
    path("companies/<slug:isin>/shareholders/", views.ShareholdersListView.as_view(), name="shareholders"),
    path("companies/<slug:isin>/liquidity/", views.LiquidityRetrieveView.as_view(), name="liquidity"),
    path("companies/<slug:isin>/statement_of_account/", views.StatementOfAccountListView.as_view(), name="statement"),
    path("companies/<slug:isin>/trades/", views.TradeCompanyListView.as_view(), name="company_trades"),
    path("companies/<slug:isin>/buyer_seller/", views.BuyerSellerListView.as_view(), name="company_buyer"),
    path("companies/<slug:isin>/orders/", views.OrderCompanyViewSet.as_view(), name="order_company"),
    path("companies/<slug:isin>/bond/", views.BondListCreateView.as_view(), name="bonds"),
    path("orders/", views.OrderListCreateAPIView.as_view(), name="orders"),
    path("orders/user/", views.UserOrderListAPIView.as_view(), name="orders_user"),
    path("trades/", views.TradeListView.as_view(), name="trades"),
    path("sidebar/", views.SidebarInfoRetrieveView.as_view(), name="sidebar"),
]

urlpatterns += router.urls
