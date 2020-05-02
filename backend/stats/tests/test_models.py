"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""
from decimal import Decimal

from django.db import IntegrityError
from django.utils import timezone

from common.test_base import BaseTestCase
from stats.models import HistoryCompanyData, CompanyVolume, PastKeyFigures, KeyFigures

from core.models import Order, Company


class HistoryCompanyDataTestCase(BaseTestCase):
    def test_company_has_a_history(self):
        self.assertTrue(HistoryCompanyData.objects.filter(company=self.company).exists())

    def test_company_can_only_have_one_model(self):
        with self.assertRaises(IntegrityError):
            HistoryCompanyData.objects.create(company=self.company)


class CompanyVolumeTestCase(BaseTestCase):
    def test_company_can_only_have_one_volume_per_day(self):
        day = timezone.now()
        CompanyVolume.objects.all().delete()

        CompanyVolume.objects.create(company=self.company, day=day)

        with self.assertRaises(IntegrityError):
            CompanyVolume.objects.create(company=self.company, day=day)


class PastKeyFiguresTestCase(BaseTestCase):
    def test_company_can_only_have_one_key_figure_per_day(self):
        day = timezone.now()
        PastKeyFigures.objects.all().delete()

        kwargs = {
            "ttoc": 100000,
            "book_value": 100000,
            "cdgr": 1,
            "free_float": 75,
            "activity": 50,
            "shares": 10000,
            "share_price": 5,
        }
        PastKeyFigures.objects.create(company=self.company, day=day, **kwargs)

        with self.assertRaises(IntegrityError):
            PastKeyFigures.objects.create(company=self.company, day=day, **kwargs)


class KeyFiguresTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.company_two = Company.objects.create(user=self.user_two, name="Two")

    def test_company_has_a_key_figure(self):
        self.assertTrue(KeyFigures.objects.filter(company=self.company).exists())

    def test_company_can_only_have_one_model(self):
        with self.assertRaises(IntegrityError):
            KeyFigures.objects.create(company=self.company)

    def test_calc_share_price_updates_to_highest_buy(self):
        current_share_price = self.company.keyfigures.share_price
        new_share_price = current_share_price + 10

        Order.objects.create(
            order_of=self.company, order_by=self.company_two, typ=Order.type_buy(), price=new_share_price, amount=1000
        )

        self.assertEqual(new_share_price, KeyFigures.calc_share_price(self.company))

    def test_calc_share_price_updates_to_lowest_sell(self):
        current_share_price = self.company.keyfigures.share_price
        new_share_price = round(current_share_price - Decimal(0.01), 2)

        self.assertNotEqual(new_share_price, 0)

        Order.objects.create(
            order_of=self.company, order_by=self.company_two, typ=Order.type_sell(), price=new_share_price, amount=1000
        )

        self.assertEqual(new_share_price, KeyFigures.calc_share_price(self.company))
