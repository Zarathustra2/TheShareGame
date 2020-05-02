"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from common.test_base import BaseTestCase
from core.models import Company, DepotPosition, Order, DynamicOrder
from periodic_tasks.orders import CentralBankOrdersTask
from users.models import User


class CentralBankOrdersTaskTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user_two = User.objects.create(username="user_two", email="UserTwo@web.de")
        self.company_two = Company.objects.create(user=self.user_two, name="Company 2")
        self.cb = Company.get_centralbank()

        DynamicOrder.objects.create(
            order_of=self.company,
            order_by=self.cb,
            amount=500,
            price=2,
            limit=1,
            dynamic_value=0.01,
            typ=Order.type_sell(),
        )

    def test_order_creation(self):
        """
        Test the centralbank creates dynamic orders for every depot position where there is no active sell order
        """

        DynamicOrder.objects.all().delete()

        CentralBankOrdersTask().run()

        self.assertEqual(DynamicOrder.objects.count(), DepotPosition.objects.filter(depot_of=self.cb).count())

    def test_orders_higher_than_share_price(self):
        self.company.keyfigures.share_price = 10
        self.company.keyfigures.save()

        self.company_two.keyfigures.share_price = 100
        self.company_two.keyfigures.save()

        DynamicOrder.objects.all().delete()
        CentralBankOrdersTask().run()

        for pair in [(self.company.id, 10), (self.company_two.id, 100)]:
            self.assertTrue(DynamicOrder.objects.filter(order_of_id=pair[0], order_by=self.cb))
            order = DynamicOrder.objects.get(order_of_id=pair[0], order_by=self.cb)

            self.assertTrue(order.price > pair[1])

    def test_centralbank_does_not_sell_all_at_once(self):
        user_three = User.objects.create(username="Three", email="Three@gmail.com")
        company_three = Company.objects.create(user=user_three, shares=1_000_000, name="Company Three")

        CentralBankOrdersTask().run()

        order = DynamicOrder.objects.get(order_of=company_three, order_by=self.cb)

        self.assertTrue(company_three.shares > order.amount)
