"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import os

from common.test_base import BaseTestCase
from periodic_tasks.key_figures import KeyFiguresTask
from periodic_tasks.tests.tests import TestReadFile
from tsg.settings import BASE_DIR


class KeyFiguresTest(BaseTestCase, TestReadFile):
    # ToDo: Create fixtures data

    def setUp(self):
        self.setup_path = os.path.join(BASE_DIR, "periodic_tasks/tests/resources/key_figures/setUp/")
        self.should_be_path = os.path.join(BASE_DIR, "periodic_tasks/tests/resources/key_figures/should_be/")
        self.read_data()

    def test_key_figures(self):
        k = KeyFiguresTask()
        k.run()
