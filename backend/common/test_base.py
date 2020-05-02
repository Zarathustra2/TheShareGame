"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import pytz
from django.db.models import Model
from django.utils import timezone
from rest_framework.test import APITestCase, APITransactionTestCase

from core.models import Company
from tsg.const import DATETIME_FORMAT
from users.models import User

NOW = timezone.now()
NOW_STR = NOW.astimezone(pytz.UTC).isoformat()

if NOW_STR.endswith("+00:00"):
    NOW_STR = NOW_STR[:-6] + "Z"

NOW_FORMAT = NOW.strftime(DATETIME_FORMAT)


class TestBaseMixin:
    """
    TestBaseMixin comes with two user objects, and a company object already.

    Furthermore, it provides two methods refresh_from_db() and next_id() which
    are helpful for testing.
    """

    company: Company
    user_two: User
    user: User
    centralbank: Company

    ONE_HUNDRED_THOUSAND = 100000

    def setUp(self):
        self.user = User.objects.create(username="A", password="password", email="A@web.de")
        self.company = Company.objects.create(name="Company", user=self.user, cash=self.ONE_HUNDRED_THOUSAND)
        self.user_two = User.objects.create(username="D", password="password", email="d@web.de")
        self.centralbank = Company.get_centralbank()

    @classmethod
    def refresh_from_db(cls, *args):
        """
        Refreshes all given objects from the database

        This is useful if you have already an object for instance a user
        object
        Then in the following of a request, the name of the user changes.
        In the user object is still the old state saved.
        To update the user object with the newest data from the database you
        can use self.refresh_from_db(user)
        """
        for model in args:
            model.refresh_from_db()

    @classmethod
    def next_id(cls, model: [Model]) -> int:
        """
        Returns the next id of a django-model which will be used
        when a new object gets created

        :param model:
        :return:
        """
        try:
            id_ = model.objects.latest("id").id
        except model.DoesNotExist:
            id_ = 0
        return id_ + 1


class BaseTestCase(TestBaseMixin, APITestCase):
    pass


class BaseTransactionTestCase(TestBaseMixin, APITransactionTestCase):
    pass
