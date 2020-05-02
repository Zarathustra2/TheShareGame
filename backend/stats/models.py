"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""
from __future__ import annotations

import datetime
import logging
from decimal import Decimal

from django.db import models
from django.db.models import Sum, Max, Min


from django.utils import timezone

from core.models import Company, DepotPosition, Order, Trade

logger = logging.getLogger(__name__)


class KeyFiguresBase(models.Model):
    """
    BaseModel for key figures of a company
    """

    company = models.ForeignKey("core.Company", on_delete=models.CASCADE)

    # A book value is determined by the value of the depot + the value of the bonds + the cash of the company.
    # It represents the current value of all assets summed up.
    # Hence it is a key figure which can easily be manipulated, for instance:
    #    One could push the price of one of his shares in his depot and the book value would rise as well.
    book_value = models.DecimalField(max_digits=40, decimal_places=2)

    # The ttoc stands for Total Turnover Capital.
    # The ttoc is a what-if key figure.
    # It calculates how much liquid a single company could get instantly if it would sell
    # its current depot.
    #
    # Bonds are valued for the price they have been bought. So the rates of the bond will be ignored.
    # Cash is valued as it is.
    # Shares are sold "down the orderbook".
    # For instance: Company A has 1_000 shares of Company B in his depot.
    # For Company-B there is a single buy order for 500 shares with 2€ per Share.
    # So this position gets valued as 1_000€ as Company A can sell immediately 500 shares but cannot sell
    # the other 500 shares as there is no buy order.
    #
    # Hence, the ttoc cannot be greater than the book value.
    ttoc = models.DecimalField(max_digits=40, decimal_places=2)

    # CDGR stands for: computational daily growth rate
    # As TheShareGame is way faster than the reality we cannot use the cagr (= Computation Daily Growth Rate).
    # Hence, we use the same forumla but with a daily base.
    #
    # It can be thought of as the growth rate that gets you from the initial investment value
    # to the ending investment value
    # if you assume that the investment has been compounding over the time period.
    # See: https://investinganswers.com/dictionary/c/compound-annual-growth-rate-cagr
    cdgr = models.DecimalField(max_digits=25, decimal_places=2, default=0)

    # Represents the current share price for the tick.
    # A share_price is the last price the shares of this company got traded at.
    share_price = models.DecimalField(max_digits=40, decimal_places=2, default=1)

    # Activity represents how active a company is buying/selling shares.
    # The larger the company is the more volume the company has to trade to have a high activity,
    # while companies with a lesser book value can trade with less volume to have the same activity.
    #
    # TODO: Implement it...
    activity = models.IntegerField(default=0)

    # The free float is a key figure, which determines how the shares are spread over the market.
    # A high free float indicates lots of shareholders while a lower free float indicates that
    # one or multiple companies hold most to all shares.

    # We calculate the free float by taking only the depot positions in consideration, which
    # make only a maximum of 20% of the company.
    free_float = models.DecimalField(max_digits=25, decimal_places=2, default=0)

    class Meta:
        db_table = "key_figures_base"
        abstract = True

    def bid(self):
        return self.company.bid()

    def ask(self):
        return self.company.ask()

    @classmethod
    def calc_book_value(cls, c: Company, bond_value: Decimal) -> Decimal:
        """
        Calculates the book value

        For an explanation of this key figure please see the book_value field
        in the KeyFiguresBase model.
        """

        depot_value = (
            c.depotposition_set.add_value()
            .filter(depot_of_id=c.id, private_depot=False)
            .aggregate(s=Sum("value"))
            .get("s", 0)
        )
        depot_value = depot_value or 0

        assert bond_value >= 0
        assert depot_value >= 0
        total = bond_value + depot_value + c.cash

        return total

    @classmethod
    def calc_free_float(cls, c: Company) -> Decimal:
        """
        Calculates the free float of a company

        For an explanation of this key figure please see the free_float field
        in the KeyFiguresBase model.
        """
        v = (
            # DepotPosition.objects.add_percentage()
            c.depotposition_set.add_percentage()
            .filter(percentage__lte=20)
            .aggregate(s=Sum("percentage"))
            .get("s", 0)
        )

        # if not a single shareholder matches the condition the queryset returns None
        v = v or 0

        logger.debug(f"Free float of {c}: {v}")
        assert v <= 100

        return v

    @classmethod
    def calc_ttoc(cls, c: Company, bond_value: Decimal, book_value: Decimal) -> Decimal:
        """
        Calculates the total turnover capital (=ttoc)
        """

        ttoc = c.cash + bond_value

        depot = c.depotposition_set.filter(private_depot=False).add_value()

        for p in depot:
            buy_total = c.orders_of.add_value().filter(typ=Order.type_buy()).aggregate(s=Sum("value")).get("s", 0)

            buy_total = buy_total or 0
            ttoc += min(buy_total, p.value)

        logger.debug(f"TTOC of {c}: {ttoc}")
        if ttoc > book_value:
            raise ValueError(f"Book value is greater than ttoc: {book_value} > {ttoc}")

        return ttoc

    @classmethod
    def calc_share_price(cls, c: Company) -> Decimal:
        """
        Calculates the share price of a company.

        Should probably move the calculation to somewhere else
        """

        # Todo: May move the setting of the share price to matching orders and whenever an order gets created
        highest_buy = c.orders_of.filter(typ=Order.type_buy()).order_by("price").values("price").first()
        lowest_sell = c.orders_of.filter(typ=Order.type_sell()).order_by("-price").values("price").first()

        curr = c.keyfigures.share_price

        if highest_buy is None and lowest_sell is None:
            return curr

        if highest_buy is not None:
            price = highest_buy.get("price")

            if price > curr:
                return price

        if lowest_sell is not None:
            price = lowest_sell.get("price")

            if price < curr:
                return price

        return curr

    @classmethod
    def calc_cdgr(cls, book_value: Decimal, c: Company) -> Decimal:
        return round(
            (
                (max(book_value, Decimal(0)) / Decimal(1000000))
                ** Decimal((1 / max((timezone.now() - c.historycompanydata.joined).days, 1)))
                - 1
            )
            * 100,
            2,
        )


class KeyFigures(KeyFiguresBase):
    """
    Model which stores the current key-figures of a company

    KeyFigures help players to evaluate the value of a company.

    Each key figure indicates something different, not a single key figure
    represents the value of a company.

    Still, we need to make sure users do not evaluate companies based on a
    single key figure. If this happens then we failed. So we need to have an
    eye on the market.
    """

    # Each company should only have one current key-figure model
    # so we change the field from ForeignKey to OneToOneField
    company = models.OneToOneField("core.Company", on_delete=models.CASCADE)

    class Meta:
        db_table = "key_figures"


class PastKeyFigures(KeyFiguresBase):
    """
    Stores the same values as KeyFigures but since the company exists
    and only for a current day.

    This makes it easier for retrieving the current key figures and makes the query faster
    because for the current key figures table only as many rows exist as companies.
    """

    # Since the PastKeyFigures only get calculated once per day
    # We also save the amount of shares of the company
    # Since they can change through capital reductions and capital raises.
    shares = models.PositiveIntegerField()

    day = models.DateField()

    class Meta:
        unique_together = ["company", "day"]
        db_table = "past_key_figures"

    @classmethod
    def past_from_current_key_figure(cls, k: KeyFigures, day: datetime = timezone.now()) -> PastKeyFigures:
        p = cls()
        p.book_value = k.book_value
        p.activity = k.activity
        p.cdgr = k.cdgr
        p.free_float = k.free_float
        p.ttoc = k.ttoc
        p.share_price = k.share_price
        p.shares = k.company.shares
        p.day = day
        p.company = k.company
        return p


class CompanyVolume(models.Model):
    """
    Model to store the volumes of a company

    buy_volume = How much the Company bought on the current day
    sell_volume = How much the company sold on the current day
    volume = How much the company was traded by others
    """

    company = models.ForeignKey("core.Company", on_delete=models.CASCADE)

    # The volume of shares this company has bought
    buy_volume = models.DecimalField(max_digits=40, decimal_places=2, default=0)

    # The volume of shares this company has sold from his depot
    sell_volume = models.DecimalField(max_digits=40, decimal_places=2, default=0)

    # The volume of shares of this company that has been bought/sold by other companies
    volume = models.DecimalField(max_digits=40, decimal_places=2, default=0)

    day = models.DateField()

    class Meta:
        unique_together = ["company", "day"]
        db_table = "company_volume"


class HistoryCompanyData(models.Model):
    """
    Model to store start values of a Company such as the day it got founded, and the
    amount of shares it started with.
    """

    company = models.OneToOneField("core.Company", on_delete=models.CASCADE)
    start_shares = models.PositiveIntegerField()
    joined = models.DateTimeField()

    class Meta:
        db_table = "company_history"
