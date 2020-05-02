"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from django.apps import AppConfig
from django.db.models.signals import post_save


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        import core.signals
        from core.models import Company

        post_save.connect(core.signals.create_models_new_company, sender=Company)
