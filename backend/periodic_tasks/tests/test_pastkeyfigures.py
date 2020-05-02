"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import os

from common.test_base import BaseTestCase
from core.models import Company
from periodic_tasks.key_figures import PastKeyFiguresTask
from periodic_tasks.tests.tests import TestReadFile
from stats.models import PastKeyFigures
from tsg.settings import BASE_DIR


class PastKeyFiguresTaskTest(BaseTestCase, TestReadFile):
    def setUp(self):
        self.setup_path = os.path.join(BASE_DIR, "periodic_tasks/tests/resources/key_figures/setUp/")
        self.read_data()
        # On creation of a company a past key figure gets created.
        # So we delete all of them for testing purpose
        PastKeyFigures.objects.all().delete()

    def test_past_key_figures(self):
        """
        Test creation of past key figures works for every company
        """

        PastKeyFiguresTask().run()

        for c in Company.objects.all():
            self.assertTrue(PastKeyFigures.objects.filter(company=c).exists())

        PastKeyFiguresTask().run()

        for c in Company.objects.all():
            self.assertEqual(PastKeyFigures.objects.filter(company=c).count(), 1)

    def test_company_without_key_figure_does_not_crash(self):

        company = Company.objects.first()
        self.assertIsNotNone(company.keyfigures)
        company.keyfigures.delete()

        PastKeyFiguresTask().run()

        for c in Company.objects.exclude(id=company.id):
            self.assertTrue(PastKeyFigures.objects.filter(company=c).exists())

        self.assertFalse(PastKeyFigures.objects.filter(company=company).exists())
