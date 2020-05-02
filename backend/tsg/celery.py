"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from __future__ import absolute_import, unicode_literals

import logging
import os

from celery import Celery, shared_task

# set the default Django settings module for the 'celery' program.
from celery.schedules import crontab

from tsg.settings import REDIS_URL

logger = logging.getLogger("Celery")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tsg.settings")

app = Celery("tsg")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings")

app.conf.broker_url = REDIS_URL

logger.info(f"Broker url: {REDIS_URL}")

app.conf.beat_schedule = {
    "5-Min": {"task": "periodic_tasks.jobs.five_minutes_jobs", "schedule": crontab(minute="*/5")},
    "Hour": {"task": "periodic_tasks.jobs.hour_jobs", "schedule": crontab(minute="*/60")},
    "Daily": {"task": "periodic_tasks.jobs.daily_jobs", "schedule": crontab(hour="*/24")},
}


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
