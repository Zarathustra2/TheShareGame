"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import os
import time
from decimal import Decimal
from typing import List, T

from django.db.models import Sum
from django.test import override_settings, TransactionTestCase, TestCase

from common.test_base import BaseTestCase
from core.models import StatementOfAccount, Company, DepotPosition, Order, Trade
from periodic_tasks.orders import OrderTask, check_orders_single_company
from periodic_tasks.tests.tests import TestReadFile
from tsg.settings import BASE_DIR
from users.models import User


@override_settings(task_eager_propagates=True, task_always_eager=True, broker_url="memory://", backend="memory")
class OrderTaskTest(TestCase):
    """
    Test case for the order matching.

    Via fixtures we load a set of data:
    - 5 Users
    - 5 Companies + Centralbank

    Every company has 1 million in cash except the company with the id 3 which has
    10 million in cash.

    Also, each company has 1,000,000 shares.

    Company id 2 has all of the shares of Company id 3,4,5,6 in his/her depot.

    Company id 4 & id 5 both hold 500,000 shares of company 2.

    """

    fixtures = ["user.yaml", "company.yaml", "depot.yaml"]

    def setUp(self) -> None:
        self.cb = Company.get_centralbank()

        # Seems when all the tests are run together then signals get triggered
        # and the centralbank depot positions get created. Hence, we
        # delete all of them so
        DepotPosition.objects.filter(depot_of=self.cb).delete()

        # Test if the data has been loaded correctly
        self.assertEqual(5, User.objects.count())
        self.assertEqual(6, Company.objects.count())
        self.check_market()

    def test_if_orders_dont_match_they_dont_get_matched(self):
        sell_order = Order.objects.create(order_by_id=4, order_of_id=2, price=2.01, amount=1_000, typ=Order.type_sell())

        buy_order = Order.objects.create(order_by_id=3, order_of_id=2, price=2, amount=1_000, typ=Order.type_buy())

        OrderTask().run()

        self.assertTrue(Order.objects.filter(id=sell_order.id).exists())
        self.assertTrue(Order.objects.filter(id=buy_order.id).exists())
        self.check_market()

    def test_if_sell_and_buy_same_company_buy_gets_deleted(self):
        sell_order = Order.objects.create(order_by_id=4, order_of_id=2, price=2, amount=1_000, typ=Order.type_sell())

        buy_order = Order.objects.create(order_by_id=4, order_of_id=2, price=2, amount=1_000, typ=Order.type_buy())

        OrderTask().run()

        self.assertTrue(Order.objects.filter(id=sell_order.id).exists())
        self.assertFalse(Order.objects.filter(id=buy_order.id).exists())
        self.check_market()

    def test_orders_matched(self):
        sell_order = Order.objects.create(order_by_id=4, order_of_id=2, price=2, amount=1_000, typ=Order.type_sell())

        buy_order = Order.objects.create(order_by_id=3, order_of_id=2, price=2, amount=1_000, typ=Order.type_buy())

        OrderTask().run()

        self.assertFalse(Order.objects.filter(id=sell_order.id).exists())
        self.assertFalse(Order.objects.filter(id=buy_order.id).exists())

        self.assertEqual(1, Trade.objects.count())
        self.assertTrue(Trade.objects.filter(buyer_id=3, seller_id=4, company_id=2, price=2, amount=1_000).exists())
        self.check_market()

    def test_sell_order_exists_if_not_fully_matched(self):
        sell_order = Order.objects.create(order_by_id=4, order_of_id=2, price=2, amount=1_000, typ=Order.type_sell())

        buy_order = Order.objects.create(order_by_id=3, order_of_id=2, price=2, amount=999, typ=Order.type_buy())

        OrderTask().run()

        self.assertFalse(Order.objects.filter(id=buy_order.id).exists())
        self.assertTrue(Order.objects.filter(id=sell_order.id).exists())
        self.assertEqual(1, Order.objects.get(id=sell_order.id).amount)
        self.check_market()

    def test_multiple_buy_orders_get_matched_by_single_sell(self):
        sell_order = Order.objects.create(order_by_id=4, order_of_id=2, price=2, amount=1_000, typ=Order.type_sell())

        buy_order_one = Order.objects.create(order_by_id=3, order_of_id=2, price=2, amount=100, typ=Order.type_buy())
        buy_order_two = Order.objects.create(order_by_id=6, order_of_id=2, price=2, amount=100, typ=Order.type_buy())

        OrderTask().run()

        for id_ in [buy_order_one.id, buy_order_two.id]:
            self.assertFalse(Order.objects.filter(id=id_).exists())

        sell_order.refresh_from_db()
        self.assertEqual(1_000 - 200, sell_order.amount)

        self.check_cash_order_fully_matched(buy_order_one)
        self.check_cash_order_fully_matched(buy_order_two)

        should_be = 1_000_000 + (200 * 2)
        self.assertEqual(should_be, Company.objects.get(id=sell_order.order_by_id).cash)

        self.check_market()

    def test_multiple_sell_orders_get_matched_by_single_buy(self):
        sell_order_one = Order.objects.create(order_by_id=4, order_of_id=2, price=2, amount=100, typ=Order.type_sell())
        sell_order_two = Order.objects.create(order_by_id=5, order_of_id=2, price=2, amount=100, typ=Order.type_sell())

        buy_order = Order.objects.create(order_by_id=6, order_of_id=2, price=2, amount=200, typ=Order.type_buy())

        OrderTask().run()

        for id_ in [sell_order_one.id, sell_order_two.id, buy_order.id]:
            self.assertFalse(Order.objects.filter(id=id_).exists())

        self.check_cash_order_fully_matched(sell_order_one)
        self.check_cash_order_fully_matched(sell_order_two)
        self.check_cash_order_fully_matched(buy_order)

        self.check_market()

    def b_test_multiple_buy_orders(self):

        amount = 10000
        sell_order_two = Order.objects.create(
            order_by_id=5, order_of_id=2, price=2, amount=amount, typ=Order.type_sell()
        )

        orders = []
        for i in range(amount):
            orders.append(Order(order_by_id=6, order_of_id=2, price=2, amount=1, typ=Order.type_buy()))

        Order.objects.bulk_create(orders)

        print("Order start")

        from django.db import connection, reset_queries
        from django.conf import settings

        settings.DEBUG = True
        reset_queries()

        start = time.time()
        OrderTask().run()
        end = time.time()
        print(end - start)
        print(len(connection.queries))
        # print(connection.queries)

        settings.DEBUG = False
        reset_queries()

    def check_cash_order_fully_matched(self, order: Order):

        # Each company has 1_000_000 in cash except the company with id 3.
        start_cash = 1_000_000 if order.order_by_id != 3 else 10_000_000

        if Order.type_sell() == order.typ:
            should_be = start_cash + (order.price * order.amount)
        else:
            should_be = start_cash - (order.price * order.amount)

        self.assertEqual(should_be, Company.objects.get(id=order.order_by_id).cash)

    def check_market(self):
        for c in Company.objects.exclude(id=self.cb.id):
            market_shares = (
                DepotPosition.objects.only("amount").filter(company=c.id).aggregate(s=Sum("amount")).get("s")
            )

            self.assertEqual(
                c.shares, market_shares, f"{c.name} has {c.shares} shares but in the market are {market_shares}"
            )
