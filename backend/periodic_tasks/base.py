"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import logging

import redis
from contextlib import contextmanager

from tsg import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL)

logger = logging.getLogger(__name__)


@contextmanager
def redis_lock(lock_name):
    """
    Yield 1 if specified lock_name is not already set in redis. Otherwise returns 0.
    """

    status = redis_client.set(lock_name, "lock", nx=True)
    try:
        yield status
    finally:
        redis_client.delete(lock_name)


class CeleryTask:
    """
    'Interface' that ensures all celery tasks have a run method
    """

    def run(self) -> None:
        raise NotImplementedError

    def lock_run(self) -> None:
        lock_id = self.get_lock_id()
        self.get_lock_and_run(lock_id, self.run)

    def get_lock_and_run(self, lock_id: str, fun: callable) -> bool:
        """
        Runs a function if the lock specified by the lock_id has been acquired.
        """
        with redis_lock(lock_id) as acquired:
            if acquired:
                fun()
                return True
            else:
                logger.warning(f"Task {self.__class__} already running. Could not acquire lock! Lock_id was: {lock_id}")
                return False

    def get_lock_id(self) -> str:
        """Returns the lock_id which is in that case the name of the class subclassing this 'Interface'"""
        return str(self.__class__)
