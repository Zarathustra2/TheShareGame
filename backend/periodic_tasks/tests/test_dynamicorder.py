"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from common.test_base import BaseTestCase
from core.models import Company, Order, DynamicOrder
from periodic_tasks.orders import DynamicOrdersTask
from users.models import User


class DynamicOrdersTaskTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user_two = User.objects.create(username="user_two", email="UserTwo@web.de")
        self.company_two = Company.objects.create(user=self.user_two, name="Company 2")

        self.cb = Company.get_centralbank()

        self.sell = DynamicOrder.objects.create(
            order_by=self.cb,
            order_of=self.company,
            price=10,
            dynamic_value=1,
            limit=5,
            amount=1000,
            typ=Order.type_sell(),
        )

        self.buy = DynamicOrder.objects.create(
            order_by=self.company,
            order_of=self.company_two,
            price=10,
            dynamic_value=1,
            limit=15,
            amount=1000,
            typ=Order.type_buy(),
        )

    def test_dynamic_orders(self):
        DynamicOrdersTask().run()

        sell_price_should_be = self.sell.price - self.sell.dynamic_value
        self.sell.refresh_from_db()
        self.assertEqual(sell_price_should_be, self.sell.price)

        buy_price_should_be = self.buy.price + self.buy.dynamic_value
        self.buy.refresh_from_db()
        self.assertEqual(buy_price_should_be, self.buy.price)

        # Test they do not go over their limit
        for _ in range(10):
            DynamicOrdersTask().run()

        self.buy.refresh_from_db()
        self.sell.refresh_from_db()
        self.assertEqual(self.buy.price, self.buy.limit)
        self.assertEqual(self.sell.price, self.sell.limit)
