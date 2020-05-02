"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from common.test_base import BaseTestCase
from periodic_tasks.rates import CalculateRates


class RatesTestCase(BaseTestCase):
    def setUp(self):
        self.task = CalculateRates()

    @classmethod
    def update_calc_rate(cls, cr, companies, cash, count_bonds, volume_bonds):
        cr.companies = companies
        cr.cash = cash
        cr.count_bonds = count_bonds
        cr.volume_bonds = volume_bonds

    def test_calc_rates(self):
        task = self.task

        # Every company starts with 1,000,000 in cash
        # This simulates the rate for when half of the money of the market is in bonds
        # Every Company could have a maximum of 10 bonds,
        # so with 10 companies a maximum 0f 100 bonds can exist in the market
        self.update_calc_rate(task, 10, 5_000_000, 56, 5_000_000)

        rate = task.calculate_rate()
        self.assertTrue(rate <= 0.9)

        # test a random value is added to the rate
        rate_second = task.calculate_rate()
        self.assertNotEqual(rate, rate_second)

        self.update_calc_rate(task, 10, 10_000_000, 0, 0)
        rate = task.calculate_rate()
        self.assertTrue(rate <= 3.3)
