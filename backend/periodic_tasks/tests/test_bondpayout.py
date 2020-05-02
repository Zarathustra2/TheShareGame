"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from datetime import timedelta
from decimal import Decimal

from freezegun import freeze_time

from common.test_base import BaseTestCase, NOW
from core.models import Bond, StatementOfAccount
from periodic_tasks.bonds import BondPayout


@freeze_time(NOW)
class BondPayoutTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.bonds = []
        time = NOW
        id_ = self.company.id
        self.bond = Bond(
            company_id=id_, value=self.ONE_HUNDRED_THOUSAND, rate=1, runtime=3, expires=(time - timedelta(days=3))
        )

        self.bond_two = Bond(
            company_id=id_, value=self.ONE_HUNDRED_THOUSAND, rate=1, runtime=3, expires=(time - timedelta(days=3))
        )

        # this one does not have the same value as the two before
        # hence it should create a new bond statement in the end
        self.bond_three = Bond(
            company_id=id_, value=self.ONE_HUNDRED_THOUSAND + 1, rate=1, runtime=3, expires=(time - timedelta(days=3))
        )

        bond_not_expiring_yet = Bond(
            company_id=id_, value=self.ONE_HUNDRED_THOUSAND, rate=1, runtime=3, expires=(time + timedelta(minutes=1))
        )

        self.bonds.append(self.bond)
        self.bonds.append(self.bond_two)
        self.bonds.append(self.bond_three)
        self.bonds.append(bond_not_expiring_yet)
        Bond.objects.bulk_create(self.bonds)

    def test_calc_rate(self):
        bond = Bond.objects.create(value=self.ONE_HUNDRED_THOUSAND, company=self.company, runtime=3, rate=1)

        value_with_rate = bond.calc_value()
        should_be = Decimal.from_float(103030.10)
        self.assertAlmostEqual(value_with_rate, should_be)

    def test_bond_payout(self):
        payout = BondPayout()

        cash_before = self.company.cash
        should_be = cash_before + self.bond.calc_value() + self.bond_two.calc_value() + self.bond_three.calc_value()

        payout.run()

        self.company.refresh_from_db()
        self.assertEqual(self.company.cash, should_be)

        statement = StatementOfAccount.objects.filter(company_id=self.company.id, typ="Bond").order_by("id")
        self.assertEqual(statement.count(), 2)

        statement = statement.first()
        self.assertEqual(statement.value, self.bond.calc_value() + self.bond_two.calc_value())
        self.assertEqual(statement.company.id, self.company.id)
        self.assertEqual(statement.amount, 2)
