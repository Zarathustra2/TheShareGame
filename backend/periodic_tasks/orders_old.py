import logging
from decimal import Decimal
from typing import Tuple

from celery import shared_task
from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone

from core.models import Company, Order, Activity, DepotPosition, Trade, StatementOfAccount, DynamicOrder
from notify.events import Event, store_event
from periodic_tasks.base import CeleryTask
from tsg.const import CENTRALBANK
from users.models import Notification, User

logger = logging.getLogger(__name__)


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

        # list of depot positions which should be deleted
        self.delete_depot_positions = list()

        # list of notifications for users that their order has been fulfilled.
        self.notfications = list()

    def run(self):
        with transaction.atomic():
            # ToDo: Is there a way to filter only those companies
            # where the ask is <= than the bid
            companies = (
                Company.objects.select_related("activity")
                .prefetch_related("orders_of")
                .all()
                .exclude(name=CENTRALBANK)
                .select_for_update()
                .exclude(activity=None)
            )

            for c in companies.iterator():
                self.check_single_company(c)

            self.bulk_update()

    def check_single_company(self, c: Company):
        buys = c.orders_of.filter(typ=Order.type_buy()).order_by("-price")
        sells = c.orders_of.filter(typ=Order.type_sell()).order_by("price")

        # These are 2 queries per company but if we would use len() then
        # the whole queryset gets evaluated
        # If someone would create thousands of small orders that could be really expensive
        # and a potential vulnerability
        buys_count = buys.count()
        sells_count = sells.count()

        i, j = 0, 0
        while i < buys_count and j < sells_count:
            buy = buys[i]
            sell = sells[j]

            # none of the orders will match for this company
            if buy.price < sell.price:
                break

            i, j = self.match_order(buy, sell, i, j)

    def match_order(self, buy: Order, sell: Order, buy_counter: int, sell_counter: int) -> Tuple[int, int]:
        # if the buying site is willing to pay more than the sell site
        # asks for, than the buy site will pay it and the sell site will receive it

        assert buy.order_of == sell.order_of

        price = buy.price
        amount = buy.amount

        if amount > sell.amount:
            amount = sell.amount

        if buy.amount == amount:
            buy_counter += 1
            self.order_ids_delete.append(buy.id)
        else:
            Order.objects.filter(id=buy.id).update(amount=F("amount") - amount)

        if sell.amount == amount:
            sell_counter += 1
            self.order_ids_delete.append(sell.id)
        else:
            Order.objects.filter(id=sell.id).update(amount=F("amount") - amount)

        # buy site should loose money
        self.update_cash_company(buy.order_by, -price)
        self.update_cash_company(sell.order_by, price)

        self.update_activity(buy.order_by)
        self.update_activity(sell.order_by)

        self.update_depot(buy, sell, price, amount)

        if buy.order_by.user:
            self.create_notification(buy.order_by.user, amount, price, buy.order_of, received=True)

        if sell.order_by.user:
            self.create_notification(sell.order_by.user, amount, price, buy.order_of, received=False)

        return buy_counter, sell_counter

    def update_cash_company(self, company: Company, cash):
        # ToDo: Update for private depot so private depot receives the money
        id_ = company.id

        if id_ not in self.companies_cash_update:
            company.cash = F("cash") + cash
            self.companies_cash_update[id_] = company
        else:
            company = self.companies_cash_update[id_]
            company.cash += cash
            self.companies_cash_update[id_] = company

    def update_depot(self, buy: Order, sell: Order, price: Decimal, amount: int):

        # ToDo: TestCase
        if not buy.order_of.id == sell.order_of.id:
            raise ValueError(f"Buy Order of was {buy.order_of}, Sell Order was of {sell.order_of}")

        buy_company = buy.order_by
        sell_company = sell.order_by
        company = buy.order_of

        # update sell site depot
        key = (sell_company.id, company.id)

        # pass negative amount so the value gets subtracted from the depot position
        obj = self._update_single_depot_position(key, -amount)

        if not obj.amount >= 0:
            raise ValueError(f"Depot position amount is {amount}")

        # All shares of this company have been sold, hence we can delete this object
        if obj.amount == 0:
            self.delete_depot_positions.append(obj.id)

        # update buy site depot
        key = (buy_company.id, company.id)
        _ = self._update_single_depot_position(key, amount)

        # check that not more shares have been accidentally generated
        # ToDo: Might be expensive. => Benchmark
        total_shares = Company.objects.only("shares").get(id=company.id).shares
        depot_total_shares = (
            DepotPosition.objects.only("amount").filter(company=company.id).aggregate(s=Sum("amount")).get("s")
        )
        if not total_shares == depot_total_shares:
            raise ValueError(f"{total_shares} != {depot_total_shares}")

        # create new trade object
        trade = Trade(buyer=buy_company, seller=sell_company, company=company, amount=amount, price=price)

        self.trades.append(trade)

        # create new statement of account objects
        value = amount * price
        self._new_statement(sell_company, amount, value, received=True)
        self._new_statement(buy_company, amount, value, received=False)

    def update_activity(self, company: Company):
        id_ = company.id

        if id_ not in self.activity_update:
            obj = company.activity.id
            self.activity_update[id_] = obj

    def bulk_update(self, batch=False):
        # ToDo: Benchmarktest, I do not know if that approach scales
        # maybe work with batch size, if 500 values in a dict, insert it and clear it

        # Either clear & insert the lists if we check for batch size
        # or clear & insert the lists if we force it
        # Normally a batch run happens during the order check after every order
        # so the data does not get to full
        # A force insert happens when all orders have been matched
        # and we want to insert the rest

        # activity
        if not batch or len(self.activity_update) > self.BATCH:
            list_ = [v for k, v in self.activity_update.items()]
            Activity.objects.filter(id__in=list_).update(updated=timezone.now())
            self.activity_update = dict()

        # update cash of companies
        if not batch or len(self.companies_cash_update) > self.BATCH:
            list_ = [v for k, v in self.companies_cash_update.items()]
            Company.objects.bulk_update(list_, ["cash"])
            self.companies_cash_update = dict()

        # delete Orders
        if not batch or len(self.order_ids_delete) > self.BATCH:
            Order.objects.filter(id__in=self.order_ids_delete).delete()
            self.order_ids_delete = list()

        # delete Positions
        if not batch or len(self.delete_depot_positions) > self.BATCH:
            DepotPosition.objects.filter(id__in=self.delete_depot_positions).delete()
            self.delete_depot_positions = ()

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

        if not batch or len(self.notfications) > self.BATCH:
            Notification.objects.bulk_create(self.notfications)
            for obj in self.notfications:
                e = Event(user_id=obj.user_id, typ="Order", msg=obj.subject)
                store_event(e)
            logger.info(f"Created {len(self.notfications)} notifcications!")
            self.notfications = list()

    def _new_statement(self, company: Company, amount: int, value: Decimal, received: bool):
        statement = StatementOfAccount(typ="Order", amount=amount, value=value, company=company, received=received)
        self.statements.append(statement)

    def create_notification(self, user: User, amount: int, price: Decimal, order_of: Company, received: bool):
        notification = Notification.order(user, amount, price, order_of, received)
        self.notfications.append(notification)

    @staticmethod
    def _update_single_depot_position(key: Tuple[int, int], amount: int) -> DepotPosition:

        # TODO: Find a better way
        obj = DepotPosition.objects.get_or_create(depot_of_id=key[0], company_id=key[1])[0]
        obj.amount = F("amount") + amount
        obj.save()

        # get rid of the CombinedExpression F
        obj.refresh_from_db()
        return obj


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
