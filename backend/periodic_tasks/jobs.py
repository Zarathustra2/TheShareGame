"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from celery.task import task

from periodic_tasks.bonds import BondPayout
from periodic_tasks.key_figures import KeyFiguresTask, PastKeyFiguresTask
from periodic_tasks.orders import OrderTask, CentralBankOrdersTask, DynamicOrdersTask
from periodic_tasks.rates import CalculateRates


@task()
def five_minutes_jobs():
    OrderTask().lock_run()
    BondPayout().lock_run()
    KeyFiguresTask().lock_run()
    CentralBankOrdersTask().lock_run()


@task()
def hour_jobs():
    CalculateRates().lock_run()
    DynamicOrdersTask().lock_run()


@task()
def daily_jobs():
    PastKeyFiguresTask().lock_run()
