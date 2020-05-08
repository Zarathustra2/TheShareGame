from datetime import timedelta
from decimal import Decimal

from django.db import IntegrityError
from freezegun import freeze_time

from common.test_base import NOW, BaseTestCase
from core.models import Bond, Company, DepotPosition, Trade, StatementOfAccount
from core.models import Order, Activity, InterestRate
from core.tasks import create_bond
from stats.models import HistoryCompanyData, CompanyVolume, KeyFigures, PastKeyFigures, KeyFiguresBase
from tsg.const import CENTRALBANK
from users.models import User


class CompanyTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.company_b = Company.objects.create(name="Company-B", user=self.user_two)

    def test_get_id_from_isin(self):
        id_ = Company.get_id_from_isin(self.company.isin)
        self.assertEqual(id_, self.company.id)

    def test_id_from_isin(self):
        id_ = self.company.id_from_isin()
        self.assertEqual(id_, self.company.id)

    def test_id_from_isin_can_hande_non_ints(self):
        self.assertEqual(Company.get_id_from_isin("abc"), -1)
        self.assertEqual(Company.get_id_from_isin("US0000001k"), -1)

    def test_get_centralbank(self):
        c = Company.get_centralbank()
        self.assertEqual(c.name, CENTRALBANK)

    def test_enough_money(self):
        self.assertTrue(self.company.enough_money(self.company.cash))
        self.assertFalse(self.company.enough_money(self.company.cash + 1))

        o = Order.objects.create(
            order_of=self.company_b, order_by=self.company, price=1, amount=100, typ=Order.type_buy()
        )
        self.assertFalse(self.company.enough_money(self.company.cash))
        self.assertTrue(self.company.enough_money(self.company.cash - (o.price * o.amount)))

    def test_bid(self):
        """Test bid returns the correct value"""
        bid = self.company.bid()
        self.assertEqual(None, bid)

        ask = self.company.ask()
        self.assertEqual(None, ask)

        Order.objects.create(order_of=self.company, order_by=self.company_b, price=1, amount=100, typ=Order.type_buy())

        Order.objects.create(order_of=self.company, order_by=self.company_b, price=1, amount=100, typ=Order.type_sell())

        bid = self.company.bid()
        self.assertDictEqual({"price": Decimal("1.00"), "total_amount": Decimal("100")}, bid)

        ask = self.company.ask()
        self.assertDictEqual({"price": Decimal("1.00"), "total_amount": Decimal("100")}, ask)

    def test_isin_creation(self):
        self.assertEqual(len(self.company.isin), 8)

    def test_isin_update(self):
        """Test companies can update the country code of the isin"""
        self.company.country = "DE"
        self.company.save(isin_update=True)
        self.company.refresh_from_db()

        should_be = self.company.isin.replace("US", "DE")
        self.assertEqual(should_be, self.company.isin)

    def test_str(self):
        self.assertEqual(str(self.company), "Company")

    def test_has_activity_model(self):
        self.assertTrue(Activity.objects.filter(company=self.company).exists())

    def test_has_history_model(self):
        self.assertTrue(HistoryCompanyData.objects.filter(company=self.company).exists())

    def test_has_volume_model(self):
        self.assertTrue(CompanyVolume.objects.filter(company=self.company).exists())

    def test_has_key_figures_model(self):
        self.assertTrue(KeyFigures.objects.filter(company=self.company).exists())

    def test_has_past_key_figure_model(self):
        self.assertTrue(PastKeyFigures.objects.filter(company=self.company).exists())

    def test_key_figures_stats_are_correct(self):
        def assert_key_figure(k: KeyFiguresBase, c: Company) -> None:
            self.assertEqual(k.book_value, c.cash)
            self.assertEqual(k.ttoc, c.cash)

            share_price = c.cash / c.shares
            self.assertEqual(k.share_price, share_price)

        for i in [1_000, 1_000_000]:
            self.user_two.company.delete()
            c = Company.objects.create(user=self.user_two, cash=1_000_000, name="Inc Invest", shares=i)
            k = c.keyfigures
            assert_key_figure(k, c)
            assert_key_figure(c.pastkeyfigures_set.first(), c)

    def test_centralbank_exists(self):
        cb = Company.get_centralbank()
        self.assertIsNotNone(cb)
        self.assertTrue(cb.name, "Centralbank")

        # Test the signals got triggerd. On migrations signals are not triggered.
        # Must be called by hand
        self.assertTrue(Activity.objects.filter(company=cb).exists())
        self.assertTrue(HistoryCompanyData.objects.filter(company=cb).exists())
        self.assertTrue(CompanyVolume.objects.filter(company=cb).exists())
        self.assertTrue(KeyFigures.objects.filter(company=cb).exists())

    def test_cannot_delete_company_if_has_depot_positions(self):
        DepotPosition.objects.create(depot_of=self.company, company=self.company_b, amount=10000, price_bought=15)
        with self.assertRaises(ValueError):
            self.company.delete()

    def test_cannot_delete_company_if_has_bonds(self):
        Bond.objects.create(company=self.company, value=100000, runtime=3, day_time_issued=NOW)
        with self.assertRaises(ValueError):
            self.company.delete()

    def test_cannot_delete_company_if_not_all_trades_have_history_model(self):
        self.trade = Trade.objects.create(buyer=self.company, seller=self.centralbank, company=self.company_b)

        with self.assertRaises(ValueError):
            self.company.delete()

    def test_bulk_delete_disabled(self):
        with self.assertRaises(NotImplementedError):
            Company.objects.all().delete()


class OrderTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.company_2 = Company.objects.create(name="B", user=self.user_two)

        self.order = Order.objects.create(
            order_by=self.company, order_of=self.company_2, price=5, amount=10000, typ=Order.type_buy()
        )

    def test_value_queryset(self):
        order = Order.objects.add_value().get(id=self.order.id)
        self.assertEqual(order.value, self.order.price * self.order.amount)

    def test_company_can_place_multiple_orders(self):
        Order.objects.create(
            order_by=self.company, order_of=self.company_2, price=5, amount=10000, typ=Order.type_buy()
        )
        self.assertEqual(Order.objects.filter(order_by=self.company, order_of=self.company_2).count(), 2)

    def test_types(self):
        """Test the Order types"""
        self.assertEqual(Order.type_buy(), "Buy")
        self.assertEqual(Order.type_sell(), "Sell")
        self.assertEqual(Order.TYPES, [("Buy", "Buy"), ("Sell", "Sell")])

    def test_type_cannot_be_empty(self):
        """Test the typ cannot be empty and must be set"""
        order = Order(order_by=self.company, order_of=self.company_2, price=5, amount=10000)
        with self.assertRaises(IntegrityError):
            order.save()

    def test_deleted_order_by_deletes_order(self):
        self.order.order_by.delete()
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_deleted_order_of_deletes_order(self):
        self.order.order_of.delete()
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())


@freeze_time(NOW)
class BondTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.bond = Bond.objects.create(company=self.company, value=100000, runtime=3, day_time_issued=NOW)

    def test_str(self):
        bond = self.bond
        self.assertEqual(str(bond), f"{bond.company}: {bond.value}")

    def test_expires_field_has_the_correct_date(self):
        should_expire = NOW + timedelta(days=3)

        def date_to_dict(date):
            """
            Because of ms difference and auto_now_add=True on the Bond model
            we will return a dict of everything besides the ms
            """
            data = dict()
            data["year"] = date.year
            data["month"] = date.month
            data["day"] = date.day
            data["hour"] = date.hour
            data["minute"] = date.minute
            return data

        should_expire_dict = date_to_dict(should_expire)
        self.assertDictEqual(should_expire_dict, date_to_dict(self.bond.expires))

    def test_create_bond(self):
        bond = create_bond(company_isin=self.company.isin, value=666, runtime=3)
        should_be = Bond.objects.get(company=self.company, value=666)
        self.assertEqual(bond, should_be)


class InterestRateTestCase(BaseTestCase):
    def test_rate_exists(self):
        self.assertEqual(InterestRate.objects.count(), 1)

    def test_latest_rate(self):
        before = InterestRate.get_latest_rate()
        InterestRate.objects.create(rate=before + 1)
        after = InterestRate.get_latest_rate()
        self.assertTrue(after > before)

    def test_calc_rate(self):
        low_rate_high_value = InterestRate.calc_rate(1_000_000)
        high_rate_low_value = InterestRate.calc_rate(500_000)
        self.assertTrue(low_rate_high_value < high_rate_low_value)


class DepotPositionTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.company_two = Company.objects.create(name="B", user=self.user_two)
        self.position = DepotPosition.objects.create(
            depot_of=self.company, company=self.company_two, amount=10000, price_bought=15
        )

    def test_str(self):
        self.assertEqual(str(self.position), f"Depot: {self.position.depot_of}, Share: {self.position.company}")

    def test_value(self):
        k = KeyFigures.objects.get(company=self.company_two)
        k.share_price = 10
        k.save()
        d = DepotPosition.objects.add_value().get(id=self.position.id)
        self.assertEqual(d.value, Decimal(k.share_price * self.position.amount))

    def test_percentage(self):
        d = DepotPosition.objects.add_percentage().get(id=self.position.id)
        self.assertEqual(d.percentage, Decimal(100 * self.position.amount / self.company_two.shares))

    def test_cannot_have_the_same_depot_position_twice(self):
        with self.assertRaises(IntegrityError):
            DepotPosition.objects.create(depot_of=self.company, company=self.company_two, amount=1, price_bought=1)


class TradeTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.company_two = Company.objects.create(name="B", user=self.user_two)
        self.user_three = User.objects.create(username="Three", email="Three@gmail.com")
        self.company_three = Company.objects.create(user=self.user_three, shares=1_000_000, name="Company Three")

        self.trade = Trade.objects.create(buyer=self.company, seller=self.company_three, company=self.company_two)

    def _create_trade_histories(self, company: Company):
        Trade.create_trade_histories(company)
        self.trade.refresh_from_db()
        t = self.trade.tradehistory
        self.assertEqual(t.company_name, self.trade.company.name)
        self.assertEqual(t.buyer_name, self.trade.buyer.name)
        self.assertEqual(t.seller_name, self.trade.seller.name)

        # Calling it a second time does not have any effect
        Trade.create_trade_histories(company)

    def test_create_trade_history_company(self):
        self._create_trade_histories(self.trade.company)

    def test_create_trade_history_seller(self):
        self._create_trade_histories(self.trade.seller)

    def test_create_trade_history_buyer(self):
        self._create_trade_histories(self.trade.buyer)

    def _deleting_company_keeps_trade(self, company: Company):
        Trade.create_trade_histories(company)
        company.delete()
        self.assertTrue(Trade.objects.filter(id=self.trade.id).exists())

    def test_deleting_company_keeps_trade(self):
        self._deleting_company_keeps_trade(self.trade.company)

    def test_deleting_seller_keeps_trade(self):
        self._deleting_company_keeps_trade(self.trade.seller)

    def test_deleting_buyer_keeps_trade(self):
        self._deleting_company_keeps_trade(self.trade.buyer)

    def test_add_value(self):
        t = Trade.objects.add_value().get(id=self.trade.id)
        self.assertEqual(t.value, t.price * t.amount)


class StatementOfAccountTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.company_two = Company.objects.create(name="B", user=self.user_two)

        self.statement_bond = StatementOfAccount.objects.create(
            company=self.company, value=1000, amount=1, received=True, typ="Bond"
        )

        self.trade = Trade.objects.create(
            seller=self.company, buyer=self.company_two, company=self.centralbank, price=5, amount=200
        )

        self.statement_order = StatementOfAccount.objects.create(
            company=self.company, value=1000, received=True, amount=200, typ="Order", trade=self.trade
        )

    def test_is_order(self):
        self.assertTrue(self.statement_order.is_order())
        self.assertFalse(self.statement_bond.is_order())

    def test_deleting_company_deletes_statement(self):
        Trade.create_trade_histories(self.company)
        self.company.delete()
        self.assertFalse(StatementOfAccount.objects.filter(company=self.company).exists())
