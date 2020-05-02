"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from unittest import TestCase

import pytest

from periodic_tasks.base import CeleryTask


class CeleryTaskTest(TestCase):
    def test_run_not_implemented(self):
        c = CeleryTask()
        with pytest.raises(NotImplementedError):
            c.run()
