"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from django.db.models import Sum

from core.models import Company, DepotPosition, Order
from tsg.const import CENTRALBANK
from users.models import User


class TestReadFile:
    # TODO Replace with fixtures

    setup_path = ""
    should_be_path = ""

    def _read_depot_positions(self, path: str):
        with open(path + "depot_positions.txt", "r") as file:
            positions = list()

            next(file)
            for line in file:
                data = line.split(",")
                company_name = data[0].strip()
                depot_of_name = data[1].strip()
                amount = int(data[2])
                company = Company.objects.get(name=company_name)
                depot_of = Company.objects.get(name=depot_of_name)
                positions.append(DepotPosition(company=company, depot_of=depot_of, amount=amount))

            # only create when we setup the data
            # we also use this function to read the should_be/depot.positions.txt file
            # and then assert
            if path == self.setup_path:
                DepotPosition.objects.bulk_create(positions)
            return positions

    def _read_orders(self, path: str):
        with open(path + "orders.txt", "r") as file:
            orders = list()

            next(file)
            for line in file:
                data = line.split(",")
                company_name = data[0].strip()
                depot_of_name = data[1].strip()
                amount = int(data[2])
                price = int(data[3])
                typ = data[4].strip().capitalize()

                assert any([typ == Order.type_buy(), typ == Order.type_sell()])

                order_of = Company.objects.get(name=company_name)
                order_by = Company.objects.get(name=depot_of_name)
                orders.append(Order(order_of=order_of, order_by=order_by, amount=amount, price=price, typ=typ))

            if self.setup_path == path:
                Order.objects.bulk_create(orders)

            return orders

    def read_companies(self, user_ids: list):
        with open(self.setup_path + "companies.txt", "r") as file:
            i = 0

            next(file)
            for line in file:
                data = line.split(",")
                name = data[0].strip()
                shares = int(data[1])
                isin = data[1].strip()
                # bulk_create does not trigger signals, could overwrite bulk_create to trigger signals
                Company.objects.create(user_id=user_ids[i], name=name, shares=shares, isin=isin)
                i += 1

    def read_users(self) -> list:
        with open(self.setup_path + "users.txt", "r") as file:
            users = list()

            # Skip comment line
            next(file)
            for line in file:
                users.append(User(username=line.strip(), email=f"{line.strip()}@web.de"))
        users = User.objects.bulk_create(users)
        user_ids = [u.id for u in users]
        return user_ids

    def read_data(self):
        user_ids = self.read_users()
        self.read_companies(user_ids)

        self._read_depot_positions(self.setup_path)
        self._read_orders(self.setup_path)

        DepotPosition.objects.filter(depot_of=Company.get_centralbank()).delete()

        # make sure that the total amount of shares of a company matches
        # the amount of shares distributed across depots in the market
        for c in Company.objects.all().exclude(name=CENTRALBANK):
            total_shares = c.shares
            total_depot_shares = DepotPosition.objects.filter(company=c).aggregate(s=Sum("amount")).get("s")
            msg = (
                f"{c} does have {total_shares} shares and {total_depot_shares} where available on the market in depots"
            )
            self.assertEqual(total_depot_shares, total_shares, msg)
