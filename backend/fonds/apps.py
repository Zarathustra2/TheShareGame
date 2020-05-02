"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save


class FondsConfig(AppConfig):
    name = "fonds"

    def ready(self):
        import fonds.signals
        from .models import Member, InvestmentFond

        post_delete.connect(fonds.signals.delete_member, sender=Member)
        post_save.connect(fonds.signals.found_fond, sender=InvestmentFond)
