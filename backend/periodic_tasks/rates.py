"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import logging
import random
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone

from core.models import Bond, Company, InterestRate
from periodic_tasks.base import CeleryTask

logger = logging.getLogger(__name__)


class CalculateRates(CeleryTask):
    """
    Calculates the rate at which the bond users can buy bonds.
    The higher the rate is, the higher the return value a user recieves for buying bonds.

    The goal is to have a high rate when not all the cash is invested in bonds
    and have a low rate when the market has invested most of its money in bonds.

    Furthermore, the rate should not be predictable, hence we should a random value to it

    The rate should be in the range of 0.3 - 2.5
    """

    def __init__(self):
        self.time = timezone.now()

        companies = Company.objects.aggregate(s=Sum("cash"), c=Count("*"))
        self.companies = companies.get("c")
        self.cash = companies.get("s")

        bonds = Bond.objects.aggregate(s=Sum("value"), c=Count("*"))
        self.count_bonds = bonds.get("c")
        self.volume_bonds = bonds.get("s")

        self.max_bonds = 10

    def run(self):

        with transaction.atomic():
            t = self.time
            rate = InterestRate.objects.filter(
                created__hour=t.hour, created__year=t.year, created__day=t.day, created__week=t.isocalendar()[1]
            )
            if rate.exists():
                logger.warning("InterestRate already exists for this hour")

            rate = self.calculate_rate()
            InterestRate.objects.create(rate=rate)

    def calculate_rate(self):

        bonds_count = self.count_bonds
        max_bonds = self.max_bonds
        volume_bonds = self.volume_bonds
        market_cash = self.cash

        fix_rate = Decimal(0.3)

        if bonds_count == 0:
            rate = 2.5
        else:

            bond_usage = round(Decimal(bonds_count / (self.companies * max_bonds)), 2)
            cash_usage = Decimal(round(volume_bonds / market_cash, 2))

            logger.info(f"bond_usage: {bond_usage}, cash_usage: {cash_usage}")

            if bond_usage == 0 or cash_usage == 0:
                rate = Decimal(2.5)
            else:
                rate = fix_rate / bond_usage / cash_usage

                logger.info(f"rate: {rate}")

                if rate > 2.5:
                    rate = Decimal(2.5)

        rate = Decimal(rate)
        rate = round((rate + rate * Decimal(random.uniform(-0.2, 0.2))) * Decimal(1.1), 2)

        logger.info(f"Final rate: {rate}")

        return rate
