"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from django.apps import AppConfig
from django.db.models.signals import post_save


class UsersConfig(AppConfig):
    name = "users"

    def ready(self):
        import users.signals
        from .models import User
        from tsg import settings

        post_save.connect(users.signals.create_private_depot, sender=User)
        post_save.connect(
            users.signals.create_models_user, sender=settings.AUTH_USER_MODEL
        )
