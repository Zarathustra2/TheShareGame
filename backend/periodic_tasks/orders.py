"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import logging
from decimal import Decimal
from typing import Tuple

from celery import shared_task
from django.db import transaction, DEFAULT_DB_ALIAS
from django.db.models import F, Sum
from django.db.transaction import Atomic, get_connection
from django.utils import timezone

from core.models import Company, Order, Activity, DepotPosition, Trade, StatementOfAccount, DynamicOrder
from notify.events import Event, store_event
from periodic_tasks.base import CeleryTask
from tsg import settings
from tsg.const import CENTRALBANK
from users.models import Notification, User

logger = logging.getLogger(__name__)


class LockedAtomicTransactionCompanyDepotPosition(Atomic):
    """
    Lock the whole company and depot position table for updating the orders
    """

    def __init__(self, savepoint=None):
        using = DEFAULT_DB_ALIAS
        super().__init__(using, savepoint)

    def __enter__(self):
        super().__enter__()

        if settings.DATABASES[self.using]["ENGINE"] != "django.db.backends.sqlite3":
            cursor = None
            try:
                cursor = get_connection(self.using).cursor()
                models = [Company, DepotPosition]
                for model in models:
                    cursor.execute("LOCK TABLE {db_table_name}".format(db_table_name=model._meta.db_table))
            finally:
                if cursor and not cursor.closed:
                    cursor.close()


class OrderTask(CeleryTask):
    """
    Task for matching Orders

    This is probably with the key_figures.py file the most complicated and crucial part of the whole code base.
    The more tests for these parts the better!
    If you have any ideas how to optimize the code, please let me know or make a pull request!

    During this task all orders of a company where the buy is greater or equal than the sell should be matched.
    Furthermore, the depot-positions as well as the cash of the companies should be updated.F

    """

    BATCH = 500

    def __init__(self):
        self.time = timezone.now()

        # list for holding new created trades for bulk_create
        self.trades = list()

        # list for holding new created statements of accounts for bulk_create
        self.statements = list()

        # dict of companies holding updated cash for bulk_update
        self.companies_cash_update = dict()

        # dict of activities for bulk_update
        self.activity_update = dict()

        # list of orders which will be deleted since the have fully been fulfilled
        self.order_ids_delete = list()

        # list of notifications for users that their order has been fulfilled.
        self.notifications = list()

        self.depot_positions_update = dict()

        self.depot_positions_create = dict()

        self.order_update = dict()

    def _update_single_depot_position(self, key: Tuple[int, int], amount: int) -> None:

        # TODO: Find a better way
        if key in self.depot_positions_update:
            self.depot_positions_update[key] += amount
            return

        if not DepotPosition.objects.filter(depot_of_id=key[0], company_id=key[1]).exists():
            if key not in self.depot_positions_create:
                self.depot_positions_create[key] = amount
            else:
                self.depot_positions_create[key] += amount
        else:
            self.depot_positions_update[key] = amount

    def run(self):
        with LockedAtomicTransactionCompanyDepotPosition():
            # ToDo: Is there a way to filter only those companies
            # where the ask is <= than the bid
            companies = Company.objects.exclude(name=CENTRALBANK)

            for c in companies.iterator():
                self.check_single_company(c)

            self.bulk_update()

            # check that not more shares have been accidentally generated
            for c in companies:
                # ToDo: Might be expensive. => Benchmark
                total_shares = Company.objects.only("shares").get(id=c.id).shares
                depot_total_shares = (
                    DepotPosition.objects.only("amount").filter(company=c.id).aggregate(s=Sum("amount")).get("s")
                )
                if not total_shares == depot_total_shares:
                    raise ValueError(f"{c}: Total shares {total_shares} != Market shares {depot_total_shares}")

    def check_single_company(self, c: Company):

        values = ["price", "amount", "order_by", "order_of", "id", "order_by__user_id", "order_of__name"]
        buys = c.orders_of.select_related("order_by").filter(typ=Order.type_buy()).order_by("-price")
        sells = c.orders_of.select_related("order_by").filter(typ=Order.type_sell()).order_by("price")
        buys = buys.values(*values)
        sells = sells.values(*values)

        buys_count = len(buys)
        sells_count = len(sells)

        i, j = 0, 0

        while i < buys_count and j < sells_count:
            buy = buys[i]
            sell = sells[j]

            # none of the orders will match for this company
            if buy["price"] < sell["price"]:
                break

            if buy["order_by"] == sell["order_by"]:
                self.order_ids_delete.append(buy["id"])
                i = i + 1
            else:
                i, j = self.match_order(buy, sell, i, j)

    def match_order(self, buy, sell, buy_counter: int, sell_counter: int) -> Tuple[int, int]:
        # if the buying site is willing to pay more than the sell site
        # asks for, than the buy site will pay it and the sell site will receive it

        assert buy["order_of"] == sell["order_of"]

        price = buy["price"]
        amount = buy["amount"]

        if amount > sell["amount"]:
            amount = sell["amount"]

        value = amount * price

        if buy["amount"] == amount:
            buy_counter += 1
            self.order_ids_delete.append(buy["id"])
        else:
            buy["amount"] -= amount
            self.order_update[buy["id"]] = buy["amount"]

        if sell["amount"] == amount:
            sell_counter += 1
            self.order_ids_delete.append(sell["id"])
        else:
            sell["amount"] -= amount
            self.order_update[sell["id"]] = sell["amount"]

        # buy site should loose money
        self.update_cash(buy["order_by"], -value)
        self.update_cash(sell["order_by"], value)

        self.update_depot(buy, sell, price, amount)

        if buy["order_by__user_id"]:
            self.create_notification(buy["order_by__user_id"], amount, price, buy["order_of__name"], received=True)

        if sell["order_by__user_id"]:
            self.create_notification(sell["order_by__user_id"], amount, price, buy["order_of__name"], received=False)

        return buy_counter, sell_counter

    def update_cash(self, company_id: int, value: Decimal):
        if company_id not in self.companies_cash_update:
            self.companies_cash_update[company_id] = value
        else:
            self.companies_cash_update[company_id] += value

    def update_depot(self, buy, sell, price: Decimal, amount: int):

        if not buy["order_of"] == sell["order_of"]:
            raise ValueError(f"Buy Order of was {buy.order_of}, Sell Order was of {sell.order_of}")

        # update sell site depot
        key = (sell["order_by"], buy["order_of"])

        # pass negative amount so the value gets subtracted from the depot position
        self._update_single_depot_position(key, -amount)

        # update buy site depot
        key = (buy["order_by"], buy["order_of"])
        self._update_single_depot_position(key, amount)

        # create new trade object
        trade = Trade(
            buyer_id=buy["order_by"], seller_id=sell["order_by"], company_id=buy["order_of"], amount=amount, price=price
        )
        self.trades.append(trade)

        # create new statement of account objects
        value = amount * price
        self._new_statement(sell["order_by"], amount, value, received=True)
        self._new_statement(buy["order_by"], amount, value, received=False)

    def bulk_update(self, batch=False):
        # ToDo: Benchmarktest, I do not know if that approach scales
        # maybe work with batch size, if 500 values in a dict, insert it and clear it

        # Either clear & insert the lists if we check for batch size
        # or clear & insert the lists if we force it
        # Normally a batch run happens during the order check after every order
        # so the data does not get to full
        # A force insert happens when all orders have been matched
        # and we want to insert the rest

        if not batch or len(self.depot_positions_create) > self.BATCH:
            l = list()
            for key in self.depot_positions_create:
                v = self.depot_positions_create[key]
                l.append(DepotPosition(depot_of_id=key[0], company_id=key[1], amount=v))

            DepotPosition.objects.bulk_create(l)
            self.depot_positions_create = dict()

        if not batch or len(self.depot_positions_update) > self.BATCH:

            for key in self.depot_positions_update:
                v = self.depot_positions_update[key]
                DepotPosition.objects.filter(depot_of_id=key[0], company_id=key[1]).update(amount=F("amount") + v)

            self.depot_positions_update = dict()

        # activity
        if not batch or len(self.activity_update) > self.BATCH:
            list_ = [v for k, v in self.activity_update.items()]
            Activity.objects.filter(id__in=list_).update(updated=timezone.now())
            self.activity_update = dict()

        # update cash of companies
        if not batch or len(self.companies_cash_update) > self.BATCH:
            l = list()
            for k, v in self.companies_cash_update.items():
                obj = Company(id=k, cash=F("cash") + v)
                l.append(obj)
                # Company.objects.filter(id=k).update(cash=F("cash")+v)

            Company.objects.bulk_update(l, ["cash"])
            self.companies_cash_update = dict()

        # delete Orders
        if not batch or len(self.order_ids_delete) > self.BATCH:
            Order.objects.filter(id__in=self.order_ids_delete).delete()
            self.order_ids_delete = list()

        if not batch or len(self.order_update) > self.BATCH:
            l = list()
            for k in self.order_update:
                obj = Order(id=k, amount=self.order_update[k])
                l.append(obj)
            Order.objects.bulk_update(l, fields=["amount"])

        # delete Positions
        if not batch:
            DepotPosition.objects.filter(amount=0).delete()

        # create trades and statement of acounts
        # For performance reason we use bulk_creates to save queries.
        # There is just a slight problem regarding the trades and the statement of accounts:
        # We want to save the trade id of the related trade in the statement of account.
        # So we create the trades first, then retrieve their ids and set them in the statement
        # of account objects before inserting them in the database.
        #
        # As we are using postgresql as our database it supports the setting of the id
        # field of objects during bulk_create. Postgresql the greatest database of all time!!!
        if not batch or len(self.trades) > self.BATCH or len(self.statements) > self.BATCH:
            Trade.objects.bulk_create(self.trades)

            i = 0
            for trade in self.trades:

                # For every trade there are 2 statement of accounts:
                # One for the buyer & one for the seller.
                self.statements[i].trade = trade
                self.statements[i + 1].trade = trade

                fst_statement = self.statements[i]
                snd_statement = self.statements[i + 1]

                if fst_statement.value != snd_statement.value or fst_statement.amount != snd_statement.amount:
                    raise ValueError(f"Statement did not match: {fst_statement} {snd_statement}")

                if trade.get_value() != fst_statement.value:
                    raise ValueError(f"Trade {trade} does not match statement: {fst_statement}")

                if trade.get_value() != snd_statement.value:
                    raise ValueError(f"Trade {trade} does not match statement: {snd_statement}")

                i += 2

            for statement in self.statements:
                assert statement.trade is not None

            StatementOfAccount.objects.bulk_create(self.statements)

            self.statements = list()
            self.trades = list()

        if not batch or len(self.notifications) > self.BATCH:
            Notification.objects.bulk_create(self.notifications)
            # for obj in self.notifications:
            #     e = Event(user_id=obj.user_id, typ="Order", msg=obj.subject)
            #     store_event(e)

            self.notifications = list()

    def _new_statement(self, company_id: int, amount: int, value: Decimal, received: bool):
        statement = StatementOfAccount(
            typ="Order", amount=amount, value=value, company_id=company_id, received=received
        )
        self.statements.append(statement)

    def create_notification(self, user_id: int, amount: int, price: Decimal, order_of_name: str, received: bool):
        notification = Notification.order(user_id, amount, price, order_of_name, received)
        self.notifications.append(notification)


@shared_task
def check_orders_single_company(company_id: int):
    """
    Checks for a single company if orders can be matched

    :param company_id:
    :return:
    """

    with transaction.atomic():
        company = Company.objects.select_for_update().get(id=company_id)
        o = OrderTask()

        def fn():
            if not o.check_single_company(company):
                logger.info(
                    f"Could not run check_orders_single_company for {company_id} as an order matching is already running!"
                )

        # As this is a shared_task and runs sperated from the normal OrderTask we have to acquire the lock
        # of the OrderTask and then run the check for a single company.
        o.get_lock_and_run(o.get_lock_id(), fn)

        # need to manually call the bulk_update method to insert the data in the database
        o.bulk_update()


class CentralBankOrdersTask(CeleryTask):
    """
    CeleryTask for the centralbank to create automatically
    orders for shares in his depot if no sell order exists for this company.

    The SellOrders are dynamic orders, hence they drop by a certain value every hour.
    Furthermore, the centralbank does not sell all shares at once.
    It creates orders with the amount being equal to 10% of the shares in the depot.

    As the centralbank holds in the beginning all shares of a company and by selling only small
    portions of shares each company in the market has a chance to get his hands on the shares.
    Also, this way the shares get more equally distributed over the market instead of one single company
    having all of them.
    """

    def run(self):
        cb = Company.get_centralbank()

        depot = DepotPosition.objects.filter(depot_of=cb)
        active_orders = Order.objects.filter(typ=Order.type_sell(), order_by=cb).values_list("order_of_id", flat=True)

        total_new_orders = 0

        logger.info(f"Checking {depot.count()} depot positions of the centralbank")

        with transaction.atomic():
            for position in depot.iterator():

                # TODO Add this into the query so we do not have to check this again
                if position.company_id in active_orders:
                    continue

                company = position.company
                # get 10% of the shares in the depot
                amount = position.amount * 0.1

                if position.amount < company.shares * 0.1:
                    amount = position.amount

                # The centralbank sell orders start always little bit over the last trade.
                # As it is a dynamic order and not a normal order
                # the price will dynamically fall every tick.
                # For more information please see the DynamicOrder model
                price = company.keyfigures.share_price * Decimal(1.5)
                dynamic_value = price * Decimal(0.01)

                # cannot bulk create because of multi inherited table
                DynamicOrder.objects.create(
                    order_by=cb,
                    order_of=company,
                    amount=amount,
                    price=price,
                    limit=0.5,
                    dynamic_value=dynamic_value,
                    typ=Order.type_sell(),
                )

                total_new_orders += 1

            logger.info(f"A total of {total_new_orders} sell orders have been created by the centralbank")


class DynamicOrdersTask(CeleryTask):
    """
    Celery task for updating the price of dynamic values
    """

    BATCH = 500

    def __init__(self):
        self.orders_list = list()

    def run(self):
        orders = DynamicOrder.objects.all()

        logger.info(f"Updating a total of {orders.count()} dynamic orders")

        with transaction.atomic():
            for order in orders.iterator():

                # If the current order is a sell order, then the price
                # should decrease. If it is a buy order, the price should increase
                # with the dynamic value.
                sign = -1 if order.typ == Order.type_sell() else 1
                new_price = order.price + (order.dynamic_value * sign)

                # TODO Delete DynamicOrder and convert to normal order
                # or filter the orders out during the query.ß
                if sign == -1 and new_price < order.limit:
                    continue

                if sign == 1 and new_price > order.limit:
                    continue

                order.price = new_price
                self.orders_list.append(order)

                self.bulk_update()

            self.bulk_update(force=True)

    def bulk_update(self, force: bool = False) -> None:
        if len(self.orders_list) > self.BATCH or force:
            DynamicOrder.objects.bulk_update(self.orders_list, ["price"])
            self.orders_list = list()
