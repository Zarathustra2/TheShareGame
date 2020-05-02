"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import logging

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from core.models import Bond, StatementOfAccount, Company
from notify.events import Event, store_event
from periodic_tasks.base import CeleryTask

from users.models import Notification

logger = logging.getLogger(__name__)


class BondPayout(CeleryTask):
    """
    Periodic Task for paying out bonds. Bonds get paid out if they extend the due time.

    Paying out involves updating companies cash, creating a bond_statement and deleting the bonds
    """

    def __init__(self):
        time = timezone.now()
        self.time = time
        self.dict_bonds = dict()
        self.notifications = list()

    def create_notification(self, user_id, amount, value):

        subject = f"{amount} Bonds paid out!"
        text = f"{amount} have been paid out. You received a total of {value}$!"
        notification = Notification(user_id=user_id, subject=subject, text=text)
        self.notifications.append(notification)

    def run(self):
        bonds = Bond.objects.prefetch_related("company").filter(expires__lte=self.time).select_for_update()
        logger.info(f"Paying out bonds, started: {self.time}")
        logger.info(f"Amount of bonds: {bonds.count()}")

        with transaction.atomic():
            dict_ = dict()
            for bond in bonds:
                payout = bond.calc_value()
                company_id = bond.company_id

                statement = StatementOfAccount(company_id=company_id, received=True, amount=1, value=payout, typ="Bond")

                # Only when company_id and payout match the amount parameter will be increased
                # otherwise create a new statement of account object
                key = (company_id, payout)
                if key in self.dict_bonds:
                    obj = self.dict_bonds[key]
                    obj.amount += 1
                    obj.value += payout
                    self.dict_bonds[key] = obj
                else:
                    self.dict_bonds[key] = statement

                # Company.objects.filter(id=company_id).update(cash=F("cash") + payout)

                # TODO: Thread-Safe?
                key = company_id
                if key in dict_:
                    obj = dict_[key]
                    obj.cash += payout
                    dict_[key] = obj
                else:
                    company = bond.company
                    company.cash = F("cash") + payout
                    dict_[key] = company

            # TODO: Batch same as in orders
            list_ = [dict_[k] for k in dict_]
            Company.objects.bulk_update(list_, ["cash"])

            statements = []
            for s in self.dict_bonds:
                obj = self.dict_bonds[s]
                self.create_notification(obj.company.user_id, obj.amount, obj.value)
                statements.append(obj)

            bonds.delete()
            StatementOfAccount.objects.bulk_create(statements)
            Notification.objects.bulk_create(self.notifications)

            # Store events in the redis database,
            # where the golang websocket worker can pick it up
            # and send them over to users if they are currently online and connected.
            for obj in self.notifications:
                event = Event(user_id=obj.user_id, typ="Bond", msg=obj.text)
                store_event(event)
