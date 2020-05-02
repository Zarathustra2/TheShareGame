"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import datetime
from datetime import timedelta

import pytest
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from freezegun import freeze_time
from pytz import UTC
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory, force_authenticate

from common.test_base import BaseTestCase
from common.test_base import NOW, NOW_FORMAT
from common.test_base import NOW_STR
from core.models import Activity, DepotPosition
from core.models import Bond
from core.models import Company, Trade, TradeHistory
from core.models import InterestRate
from core.models import Order
from core.models import StatementOfAccount
from tsg.const import CENTRALBANK
from tsg.const import DATETIME_FORMAT
from tsg.const import START_CASH
from users.models import User


@freeze_time(NOW)
class CompanyApiTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user_b = User.objects.create(username="B", password="password", email="B@web.de")
        self.company_b = Company.objects.create(name="Company-B", user=self.user_b)

        DepotPosition.objects.filter(depot_of=Company.get_centralbank()).delete()

        self.company_as_shareholder = DepotPosition.objects.create(
            company=self.company, depot_of=self.company_b, price_bought=1, amount=10000
        )

        self.user_company_private_depot = DepotPosition.objects.create(
            company=self.company, depot_of=self.company_b, price_bought=1, amount=10000, private_depot=True
        )

    def test_url(self):
        """Test the GET method for a company page"""
        url = self.company.get_absolute_url()
        client = self.client
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_companies_url(self):
        """Test the GET method for the companies page"""
        url = reverse("core:companies")

        with self.assertNumQueries(2):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.maxDiff = None

            should_be = {
                "count": 3,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "isin": self.company_b.isin,
                        "id": self.company_b.id,
                        "name": "Company-B",
                        "country": "US",
                        "cash": 0,
                        "shares": 1000000,
                        "user": {"id": self.company_b.user_id, "username": "B"},
                    },
                    {
                        "isin": self.company.isin,
                        "id": self.company.id,
                        "name": "Company",
                        "country": "US",
                        "cash": 100_000.0,
                        "shares": 1000000,
                        "user": {"id": self.company.user_id, "username": "A"},
                    },
                    {
                        "isin": self.centralbank.isin,
                        "id": self.centralbank.id,
                        "name": "Centralbank",
                        "country": "US",
                        "cash": 1000000.0,
                        "shares": 1000000,
                        "user": None,
                    },
                ],
            }

            self.assertDictEqual(response.json(), should_be)

    def test_get_active_company(self):
        """
        Test the GET method for the ActiveCompanyRetrieveView
        It should return a company for the current user
        """
        url = reverse("core:active_company")
        user = User.objects.create(username="WithoutCompany", password="A", email="WithoutCompany@web.de")
        client = self.client

        client.force_authenticate(user=user)
        response = client.get(url)
        self.assertEqual(response.status_code, 404)

        client.force_authenticate(user=self.user)

        with self.assertNumQueries(1):
            response = client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_depot(self):
        """Test the GET method for the depot page of a company"""
        url = reverse("core:depot-list", kwargs={"isin": self.company_b.isin})
        client = self.client

        with self.assertNumQueries(3):
            response = client.get(url)

            self.assertEqual(response.status_code, 200)

            should_be = {
                "company_name": "Company-B",
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "company": {
                            "name": "Company",
                            "user_id": self.user.id,
                            "isin": self.company.isin,
                            "id": self.company.id,
                        },
                        "amount": 10000,
                        "price_bought": 1.00,
                        "created": NOW_FORMAT,
                        "id": self.company_as_shareholder.id,
                        "share_price": 0.1,
                    }
                ],
            }

            self.assertDictEqual(should_be, response.json())

        url = reverse("core:depot-list", kwargs={"isin": 1})
        response = client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_slim_depot(self):
        url = reverse("core:depot-slim", kwargs={"isin": self.company_b.isin})
        client = self.client

        with self.assertNumQueries(1):
            response = client.get(url)

            self.assertEqual(response.status_code, 200)

            should_be = [{"name": "Company", "value": 1000.0}]

            self.assertListEqual(should_be, response.json())

    def test_shareholder(self):
        """Test the GET method for the shareholders page of a company"""
        url = reverse("core:shareholders", kwargs={"isin": self.company.isin})
        client = self.client

        with self.assertNumQueries(1):
            response = client.get(url)

            self.assertEqual(response.status_code, 200)

            should_be = [
                {
                    "amount": 10000,
                    "price_bought": 1.00,
                    "created": NOW_FORMAT,
                    "private_depot": True,
                    "id": self.user_company_private_depot.id,
                },
                {
                    "depot_of": {
                        "name": "Company-B",
                        "user_id": self.user_b.id,
                        "isin": self.company_b.isin,
                        "id": self.company_b.id,
                    },
                    "amount": 10000,
                    "price_bought": 1.00,
                    "created": NOW_FORMAT,
                    "private_depot": False,
                    "id": self.company_as_shareholder.id,
                },
            ]

            self.assertListEqual(should_be, response.json())

        url = reverse("core:shareholders", kwargs={"isin": 1})
        response = client.get(url)
        self.assertEqual(response.json(), [])

    def test_liquidity(self):
        """Test the GET method for the liquidity page of a company"""
        url = reverse("core:liquidity", kwargs={"isin": self.company_b.isin})
        client = self.client
        self.company_b.cash = 10000
        self.company_b.save()

        Bond.objects.create(company=self.company_b, value=1000, rate=1, runtime=1)

        with self.assertNumQueries(1):
            response = client.get(url)

            self.assertEqual(response.status_code, 200)

            should_be = {"cash": 10000.0, "bonds": 1000.0, "depot_value": 2000.0}

            self.assertDictEqual(should_be, response.json())

        url = reverse("core:liquidity", kwargs={"isin": "not-valid-isin"})

        response = client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_first_company_creation(self):
        """Test that users who do not have a company can create one"""
        user = User.objects.create(username="Max", email="Max@web.de")
        self.assertFalse(Company.objects.filter(user=user).exists())

        data = {"name": "Max Inc.", "country": "GE", "shares": 10_000, "cash": 1_000_000}
        self.client.force_authenticate(user=user)
        response = self.client.post(reverse("core:companies"), data)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Company.objects.filter(user=user).exists())

        company = Company.objects.get(user=user)
        self.assertEqual(company.name, "Max Inc.")
        self.assertEqual(company.shares, 10_000)
        self.assertEqual(company.country, "GE")
        self.assertEqual(company.cash, START_CASH)

    def test_users_who_have_a_company_cannot_found_a_second(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "Another Max Inc.", "country": "GE", "shares": 10_000}
        response = self.client.post(reverse("core:companies"), data)
        self.assertEqual(response.status_code, 400)

    def test_company_creation_shares_validation(self):
        self.user.company.delete()

        for i in [999, 1_000_001]:

            self.client.force_authenticate(user=self.user)
            data = {"name": "Error Inc.", "country": "GE", "shares": i}
            response = self.client.post(reverse("core:companies"), data)
            self.assertEqual(response.status_code, 400)
            self.assertDictEqual(response.json(), {"shares": ["Shares need to be between 1,000 and 1,000,000"]})

    def test_company_name_unique(self):
        user = User.objects.create(username="Max", email="Max@web.de")

        self.client.force_authenticate(user=user)
        data = {"name": self.company.name, "country": "GE", "shares": 1_000}
        response = self.client.post(reverse("core:companies"), data)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"name": ["company with this name already exists."]})


@freeze_time(NOW)
class ActivityApiTest(BaseTestCase):
    def test_activity_exists(self):
        self.assertTrue(Activity.objects.filter(company=self.company).exists())

    def test_update_activity(self):
        with freeze_time("2012-01-01 12:00:01"):
            self.company.update_activity()
            obj = Activity.objects.get(company=self.company)
            should_be = datetime.datetime(2012, 1, 1, 12, 0, 1, tzinfo=UTC)
            self.assertEqual(obj.updated, should_be)

    def test_buying_bond_updates_activity(self):
        # change time to the past so we can see an effect in the update function
        with freeze_time("2012-01-01 12:00:01"):
            url = reverse("core:bonds", kwargs={"isin": self.company.isin})
            client = self.client

            data = {"amount": 1, "value": self.ONE_HUNDRED_THOUSAND, "runtime": 3}

            client.force_authenticate(user=self.company.user)
            response = client.post(url, data=data, format="json")

            # test that the request worked
            self.assertEqual(response.status_code, 201)

            obj = Activity.objects.get(company=self.company)
            should_be = datetime.datetime(2012, 1, 1, 12, 0, 1, tzinfo=UTC)
            self.assertEqual(obj.updated, should_be)


@freeze_time(NOW)
@pytest.mark.celery
@override_settings(task_eager_propagates=True, task_always_eager=True, broker_url="memory://", backend="memory")
class OrderApiTest(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.company_2 = Company.objects.create(name="B", user=self.user_two)

        self.order = Order.objects.create(
            order_by=self.company, order_of=self.company_2, price=5, amount=10000, typ=Order.type_buy()
        )

        self.url = reverse("core:orders")

    def test_orders_returns_most_recent_orders(self):
        url = reverse("core:orders")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data = response.json().get("results")
        should_be = [
            {
                "order_of": {
                    "name": "B",
                    "user_id": self.user_two.id,
                    "isin": self.company_2.isin,
                    "id": self.company_2.id,
                },
                "typ": "Buy",
                "price": 5.00,
                "amount": 10000,
                "created": NOW_FORMAT,
                "id": self.order.id,
                "value": 50000,
            }
        ]

        self.assertListEqual(data, should_be)

    def test_orders_can_be_deleted(self):
        url = reverse("core:order_company", kwargs={"isin": self.company.isin})
        client = self.client
        data = {"order_id": self.order.id}

        client.force_authenticate(user=None)
        response = client.delete(url, data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Order.objects.count(), 1)

        client.force_authenticate(user=self.user_two)
        client.delete(url, data)
        self.assertEqual(Order.objects.count(), 1)

        client.force_authenticate(user=self.user)
        response = client.delete(url, data)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Order.objects.count(), 0)

    def test_orders_can_be_created_company_url(self):

        # Update the url so we can use the same creation tests for this endpoint
        # as they behave the same
        old_url = self.url
        self.url = reverse("core:order_company", kwargs={"isin": self.company_2.isin})
        self.test_orders_can_be_created()

        # Back to the old settings too make sure we don't break any other tests
        self.url = old_url

    def test_orders_can_be_created(self):
        # url = reverse("core:order_company", kwargs={"isin": self.company_2.isin})
        url = self.url
        client = self.client
        data = {
            "typ": "Buy",
            "price": 5,
            "amount": 1000,
            "order_by_isin": self.company.isin,
            "order_of_isin": self.company_2.isin,
        }
        should_be = {
            "order_of": {
                "name": "B",
                "user_id": self.user_two.id,
                "isin": self.company_2.isin,
                "id": self.company_2.id,
            },
            "typ": "Buy",
            "price": 5.00,
            "amount": 1000,
            "created": NOW_FORMAT,
            "id": self.next_id(Order),
        }

        client.force_authenticate(user=self.company.user)
        response = client.post(url, data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(response.json(), should_be)

        # not enough cash
        data = {
            "typ": "Buy",
            "price": 100,
            "amount": 1000000,
            "order_by_isin": self.company.isin,
            "order_of_isin": self.company_2.isin,
        }
        response = client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"non_field_errors": ["You do not have enough Cash"]})

    def test_typ_must_be_either_buy_or_sell(self):
        url = reverse("core:order_company", kwargs={"isin": self.company_2.isin})
        self.client.force_authenticate(user=self.user)
        false_data = {
            "order_by_isin": self.company.isin,
            "price": 2,
            "amount": 1000,
            "typ": "INVALID-Type",
            "order_of_isin": self.company_2.isin,
        }
        response = self.client.post(url, data=false_data, format="json")
        self.assertDictEqual(response.json(), {"typ": ['"INVALID-Type" is not a valid choice.']})

    def test_amount_must_be_greater_than_zero(self):
        url = reverse("core:order_company", kwargs={"isin": self.company_2.isin})
        self.client.force_authenticate(user=self.user)
        false_data = {
            "order_by_isin": self.company.isin,
            "price": 2,
            "amount": -1,
            "typ": "Buy",
            "order_of_isin": self.company_2.isin,
        }
        response = self.client.post(url, data=false_data, format="json")
        self.assertDictEqual(response.json(), {"amount": ["Ensure this value is greater than or equal to 0."]})

    def test_not_enough_money(self):
        url = reverse("core:order_company", kwargs={"isin": self.company_2.isin})
        self.client.force_authenticate(user=self.user)
        false_data = {"price": 20000, "amount": 10000, "typ": "Buy", "order_of_isin": self.company_2.isin}
        response = self.client.post(url, data=false_data, format="json")
        self.assertDictEqual(response.json(), {"non_field_errors": ["You do not have enough Cash"]})

    def test_price_cannot_be_negative(self):
        url = reverse("core:order_company", kwargs={"isin": self.company_2.isin})
        self.client.force_authenticate(user=self.user)
        false_data = {"price": -1, "amount": 1, "typ": "Buy", "order_of_isin": self.company_2.isin}
        response = self.client.post(url, data=false_data, format="json")
        self.assertDictEqual(response.json(), {"price": ["Price cannot be equal or less than 0"]})

    def test_cannot_sell_if_not_enough_shares_in_depot(self):
        d = DepotPosition.objects.create(company=self.company_2, depot_of=self.company, amount=1000)
        url = reverse("core:order_company", kwargs={"isin": self.company_2.isin})
        self.client.force_authenticate(user=self.user)

        false_data = {"price": 1, "amount": d.amount + 1, "typ": "Sell", "order_of_isin": self.company_2.isin}
        response = self.client.post(url, data=false_data, format="json")
        self.assertDictEqual(
            response.json(), {"amount": ["You only have 1000 shares in your depot but want to sell 1001!"]}
        )

    def test_orders_of_company(self):
        """
        Test the GET method for the order of a compay
        Should all current buy and sell orders of a company
        """
        url = reverse("core:order_company", kwargs={"isin": self.company_2.isin})
        client = self.client

        response = client.get(url)

        should_be = [
            {
                "order_of": {
                    "name": "B",
                    "user_id": self.user_two.id,
                    "isin": self.company_2.isin,
                    "id": self.company_2.id,
                },
                "typ": "Buy",
                "price": 5.00,
                "amount": 10000,
                "created": NOW_FORMAT,
                "value": 50000.00,
                "id": self.order.id,
            }
        ]

        self.assertListEqual(response.json().get("results"), should_be)

    def test_orders_of_user(self):
        """
        Test the GET method of the orders_user page
        Should return the the created orders of the user
        """
        url = reverse("core:orders_user")
        client = self.client

        client.force_authenticate(user=None)
        response = client.get(url)
        self.assertEqual(response.status_code, 401)

        client.force_authenticate(user=self.user)
        response = client.get(url)
        should_be = [
            {
                "order_of": {
                    "name": "B",
                    "user_id": self.user_two.id,
                    "isin": self.company_2.isin,
                    "id": self.company_2.id,
                },
                "typ": "Buy",
                "price": 5.00,
                "amount": 10000,
                "created": NOW_FORMAT,
                "id": self.order.id,
                "value": 50000,
            }
        ]

        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.json().get("results"), should_be)

        client.force_authenticate(user=self.user_two)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.json().get("results"), [])


@freeze_time(NOW)
class BondApiTest(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.url = reverse("core:bonds", kwargs={"isin": self.company.isin})

    def test_bonds_page_of_company_returns_data(self):
        """Test the GET method of the bonds page"""
        bond = Bond.objects.create(value=1, company=self.company, rate=2.5, runtime=3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        should_be = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "value": 1.0,
                    "rate": 2.50,
                    "runtime": 3,
                    "expires": (NOW + timedelta(days=3)).strftime(DATETIME_FORMAT),
                    "id": bond.id,
                }
            ],
        }
        self.assertDictEqual(should_be, response.json())

    def test_company_can_buy_bonds(self):
        url = self.url
        client = self.client

        data = {"amount": 1, "value": self.company.cash, "runtime": 3, "company_isin": self.company.isin}

        client.force_authenticate(user=self.company.user)

        cash_before = self.company.cash

        response = client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, 201)

        qs = Bond.objects
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.filter(company_id=self.company.id).count(), 1)
        self.assertEqual(qs.filter(company_id=self.company.id).first().value, self.ONE_HUNDRED_THOUSAND)

        cash_now = cash_before - self.ONE_HUNDRED_THOUSAND
        self.refresh_from_db(self.company)

        self.assertTrue(self.company.cash < cash_before)
        self.assertEqual(self.company.cash, cash_now)

    def test_company_cannot_buy_bonds_if_not_enough_money(self):
        url = self.url
        client = self.client
        data = {"amount": 1, "value": 100000000, "runtime": 3}

        client.force_authenticate(user=self.company.user)
        response = client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, 400)

    def test_company_cannot_buy_more_than_limit(self):
        """
        Test the POST method does not allow the creation of
        more than a total of 10 bonds
        """
        url = self.url
        client = self.client

        data = {"amount": 11, "value": 1000, "runtime": 3}

        client.force_authenticate(user=self.company.user)
        response = client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, 400)

    def test_cannot_buy_for_other_company(self):
        other_user = User.objects.create_user(username="dummy", password="dummy", email="dummy@web.de")
        company = Company.objects.create(user=other_user, name="AnotherShare")
        client = self.client
        url = reverse("core:bonds", kwargs={"isin": company.isin})

        data = {"amount": 1, "value": 1000, "runtime": 3}
        client.force_authenticate(user=self.company.user)
        response = client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, 404)


@freeze_time(NOW)
class InterestRateApiTestCase(TestCase):
    def test_url(self):
        """
        Test the GET method of the rate url
        Should return the most recent rate
        """
        obj = InterestRate.objects.create(rate=2.5)
        url = reverse("core:rate-latest")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        should_be = {"rate": 2.50, "created": NOW_STR, "id": obj.id}

        self.assertDictEqual(should_be, response.json())

    def test_chart_url(self):
        """
        Test the GET method for the rate chart
        Should return the most recent rates
        """

        # First rate is created during database migration. That happens a little
        # before the date gets freezed. So this will not be asserted correctly.
        InterestRate.objects.all().delete()

        should_be = []
        for i in range(10):
            obj = InterestRate.objects.create(rate=i)
            should_be.append({"rate": obj.rate, "created": NOW_STR, "id": obj.id})

        should_be.reverse()
        url = reverse("core:rate-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertListEqual(response.json(), should_be)


@freeze_time(NOW)
class TradeApiTestCase(TestCase):
    def setUp(self):
        self.company_1 = Company.objects.create(name="A")
        self.company_2 = Company.objects.create(name="B")
        self.company_3 = Company.objects.create(name="C")

        self.trade = Trade.objects.create(buyer=self.company_1, seller=self.company_2, company=self.company_3)

        self.trade_private = Trade.objects.create(
            buyer=self.company_1, seller=self.company_3, company=self.company_2, buyer_pd=True, seller_pd=True
        )

    def test_trade_list_view(self):
        """Test the GET method for the trades page of a company"""
        url = reverse("core:company_trades", kwargs={"isin": self.company_2.isin})
        client = self.client

        response = client.get(url)

        self.assertEqual(response.status_code, 200)

        should_be = [
            {
                "buyer": {"name": "A", "user_id": None, "isin": self.company_1.isin, "id": self.company_1.id},
                "seller": {"name": "B", "user_id": None, "isin": self.company_2.isin, "id": self.company_2.id},
                "company": {"name": "C", "user_id": None, "isin": self.company_3.isin, "id": self.company_3.id},
                "price": 0.00,
                "amount": 1,
                "price_bought": 1.00,
                "created": NOW_FORMAT,
                "buyer_pd": False,
                "seller_pd": False,
                "value": 0.00,
                "id": self.trade.id,
                "history": {},
            }
        ]

        self.assertListEqual(response.json().get("results"), should_be)

    def test_buyer_seller_view(self):
        """Test the GET method for the buyer and seller page for a company"""
        url = reverse("core:company_buyer", kwargs={"isin": self.company_3.isin})
        client = self.client

        response = client.get(url)

        self.assertEqual(response.status_code, 200)

        should_be = [
            {
                "buyer": {"name": "A", "user_id": None, "isin": self.company_1.isin, "id": self.company_1.id},
                "seller": {"name": "B", "user_id": None, "isin": self.company_2.isin, "id": self.company_2.id},
                "company": {"name": "C", "user_id": None, "isin": self.company_3.isin, "id": self.company_3.id},
                "price": 0.00,
                "amount": 1,
                "price_bought": 1.00,
                "created": NOW_FORMAT,
                "buyer_pd": False,
                "seller_pd": False,
                "value": 0.00,
                "id": self.trade.id,
                "history": {},
            }
        ]

        self.assertListEqual(response.json().get("results"), should_be)

    def test_trade_pd(self):
        """Test the GET method for the trades page of the private depot page"""
        # ToDo: Remove isin from url
        url = reverse("core:company_trades", kwargs={"isin": self.company_3.isin})
        client = self.client

        response = client.get(url)

        # private trades should not be visible in the trades list view
        self.assertEqual(response.json().get("results"), [])

        url = reverse("core:company_buyer", kwargs={"isin": self.company_2.isin})

        response = client.get(url)

        should_be = [
            {
                "company": {"name": "B", "user_id": None, "isin": self.company_2.isin, "id": self.company_2.id},
                "price": 0.00,
                "amount": 1,
                "price_bought": 1.00,
                "created": NOW_FORMAT,
                "buyer_pd": True,
                "seller_pd": True,
                "value": 0.00,
                "id": self.trade_private.id,
                "history": {},
            }
        ]

        self.assertListEqual(response.json().get("results"), should_be)

    def test_all_trades(self):
        """Test the trades url returns all trades paginated"""
        url = reverse("core:trades")

        response = self.client.get(url)

        should_be = {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "company": {"name": "B", "user_id": None, "isin": self.company_2.isin, "id": self.company_2.id},
                    "price": 0.00,
                    "amount": 1,
                    "price_bought": 1.00,
                    "created": NOW_FORMAT,
                    "buyer_pd": True,
                    "seller_pd": True,
                    "value": 0.00,
                    "id": self.trade_private.id,
                    "history": {},
                },
                {
                    "buyer": {"name": "A", "user_id": None, "isin": self.company_1.isin, "id": self.company_1.id},
                    "seller": {"name": "B", "user_id": None, "isin": self.company_2.isin, "id": self.company_2.id},
                    "company": {"name": "C", "user_id": None, "isin": self.company_3.isin, "id": self.company_3.id},
                    "price": 0.00,
                    "amount": 1,
                    "price_bought": 1.00,
                    "created": NOW_FORMAT,
                    "buyer_pd": False,
                    "seller_pd": False,
                    "value": 0.00,
                    "id": self.trade.id,
                    "history": {},
                },
            ],
        }

        self.assertEqual(200, response.status_code)
        self.assertDictEqual(should_be, response.json())

        tr = Trade.objects.create(amount=10000, price=5.56, price_bought=2,)

        t = TradeHistory.objects.create(
            buyer_name="Ramm Inc.", seller_name="Cool Inc.", company_name="Comp Inc.", trade=tr
        )

        t_json = {
            "buyer": None,
            "seller": None,
            "company": None,
            "price": 5.56,
            "amount": 10000,
            "price_bought": 2.00,
            "created": NOW_FORMAT,
            "buyer_pd": False,
            "seller_pd": False,
            "value": 55600.00,
            "id": tr.id,
            "history": {"buyer_name": t.buyer_name, "seller_name": t.seller_name, "company_name": t.company_name},
        }

        should_be["results"].insert(0, t_json)
        should_be["count"] += 1

        response = self.client.get(url)
        self.assertDictEqual(should_be, response.json())


@freeze_time(NOW)
class StatementOfAccountApiTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.company_two = Company.objects.create(name="B")

        self.statement_bond = StatementOfAccount.objects.create(
            company=self.company, value=1000, amount=1, received=True, typ="Bond"
        )

        self.trade = Trade.objects.create(
            seller=self.company, buyer=self.company_two, company=self.centralbank, price=5, amount=200
        )

        self.statement_order = StatementOfAccount.objects.create(
            company=self.company, value=1000, received=True, typ="Order", trade=self.trade, amount=self.trade.amount
        )

    def test_url(self):
        """Test the GET method for the statement url for a company"""
        url = reverse("core:statement", kwargs={"isin": self.company.isin})
        client = self.client
        response = client.get(url)

        self.assertEqual(response.status_code, 200)

        should_be = [
            {
                "company": {
                    "name": "Company",
                    "user_id": self.user.id,
                    "isin": self.company.isin,
                    "id": self.company.id,
                },
                "typ": "Order",
                "value": 1000.00,
                "received": True,
                "created": NOW_FORMAT,
                "id": self.statement_order.id,
                "amount": 200,
                "trade": {
                    "buyer": {
                        "name": self.company_two.name,
                        "user_id": None,
                        "isin": self.company_two.isin,
                        "id": self.company_two.id,
                    },
                    "seller": {
                        "name": self.company.name,
                        "user_id": self.company.user_id,
                        "isin": self.company.isin,
                        "id": self.company.id,
                    },
                    "company": {
                        "name": Company.get_centralbank().name,
                        "user_id": None,
                        "isin": Company.get_centralbank().isin,
                        "id": Company.get_centralbank().id,
                    },
                    "price": self.trade.price,
                    "amount": self.trade.amount,
                    "price_bought": self.trade.price_bought,
                    "created": NOW_FORMAT,
                    "buyer_pd": False,
                    "seller_pd": False,
                    "value": self.trade.get_value(),
                    "id": self.trade.id,
                    "history": {},
                },
            },
            {
                "company": {
                    "name": "Company",
                    "user_id": self.user.id,
                    "isin": self.company.isin,
                    "id": self.company.id,
                },
                "typ": "Bond",
                "value": 1000.00,
                "received": True,
                "created": NOW_FORMAT,
                "id": self.statement_bond.id,
                "amount": 1,
            },
        ]

        self.assertListEqual(should_be, response.json().get("results"))


class SidebarApiTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        Order.objects.create(
            typ=Order.type_sell(), order_by=Company.get_centralbank(), order_of=self.company, price=2, amount=100
        )

    def test_sidebar(self):
        url = reverse("core:sidebar")
        rsp = self.client.get(url)

        cb = Company.get_centralbank()
        should_be = {
            "companies": [
                {
                    "name": self.company.name,
                    "isin": self.company.isin,
                    "id": self.company.id,
                    "share_price": float(self.company.keyfigures.share_price),
                },
                {"name": cb.name, "isin": cb.isin, "id": cb.id, "share_price": float(cb.keyfigures.share_price)},
            ],
            "bond_rate": float(InterestRate.get_latest_rate()),
            "companies_count": Company.objects.count(),
            "buy_orders_count": Order.objects.filter(typ=Order.type_buy()).count(),
            "sell_orders_count": Order.objects.filter(typ=Order.type_sell()).count(),
        }

        self.assertDictEqual(should_be, rsp.json())
