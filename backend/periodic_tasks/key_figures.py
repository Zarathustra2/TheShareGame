"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum, Max, Min
from django.utils import timezone

from core.models import Company, DepotPosition, Order, Trade
from periodic_tasks.base import CeleryTask
from stats.models import KeyFigures, PastKeyFigures
from tsg.const import CENTRALBANK

logger = logging.getLogger(__name__)


class KeyFiguresTask(CeleryTask):
    """
    Updates the key figures of all companies

    This is probably with the orders.py file the most complicated and crucial part of the whole code base.
    The more tests for these parts the better!
    If you have any ideas how to optimize the code, please let me know or make a pull request!

    Todo: Task could be optimized if we only iterate over the companies where data changed.
            But I am not sure if it is worth the effort

    """

    BATCH = 500

    def __init__(self):
        self.key_figures = list()

    def run(self):
        with transaction.atomic():
            for c in (
                Company.objects.select_related("keyfigures")
                .prefetch_related("depotposition_set", "bond_set", "orders_of")
                .all()
                .iterator()
            ):

                # each company has per default a key_figure object from the start on
                # see company_signals
                k = c.keyfigures

                # Not all companies have bonds, the queryset evaluation would return
                # none if it does not have companies. So we use  the "or" operator to return 0 in that case
                bond_value = c.bond_set.aggregate(s=Sum("value")).get("s", 0) or 0
                k.book_value = KeyFigures.calc_book_value(c, bond_value)
                k.activity = k.activity
                k.cdgr = KeyFigures.calc_cdgr(k.book_value, c)
                k.free_float = KeyFigures.calc_free_float(c)
                k.ttoc = KeyFigures.calc_ttoc(c, bond_value, k.book_value)
                k.share_price = KeyFigures.calc_share_price(c)

                self.key_figures.append(k)

                if len(self.key_figures) > self.BATCH:
                    self.insert_in_db()

            self.insert_in_db()

    def insert_in_db(self):
        KeyFigures.objects.bulk_update(
            self.key_figures, ["book_value", "activity", "cdgr", "free_float", "ttoc", "share_price"]
        )
        self.key_figures = list()


class PastKeyFiguresTask(CeleryTask):
    """
    Saves the key figures of a company for a specific day
    """

    BATCH = 500

    def __init__(self):
        self.day = timezone.now()
        self.past_key_figures = list()

    def run(self):
        with transaction.atomic():

            companies = Company.objects.select_related("keyfigures").filter(keyfigures__isnull=False).iterator()

            for c in companies:
                curr = c.keyfigures

                # TODO: Filter those companies out that do not have a pastkeyfigure already for that day
                # in the first query, so we dont query for each company.
                if not PastKeyFigures.objects.filter(company=c, day=self.day).exists():
                    # Copy current key figures
                    p = PastKeyFigures.past_from_current_key_figure(curr, self.day)
                    self.past_key_figures.append(p)

                    if len(self.past_key_figures) > self.BATCH:
                        self.insert_in_db()

            self.insert_in_db()

    def insert_in_db(self) -> None:
        PastKeyFigures.objects.bulk_create(self.past_key_figures)
        self.past_key_figures = list()
