"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from rest_framework.authtoken.models import Token

from core.models import PrivateDepot
from users.models import Profile, Conversation


def create_private_depot(sender, instance, created, **kwargs):
    if created:
        user = instance
        PrivateDepot.objects.get_or_create(user=user)


def create_models_user(sender, instance=None, created=False, **kwargs):
    """
    Create an API-Token for Users upon Registration
    """
    if created:
        Token.objects.create(user=instance)
        Profile.objects.create(user=instance, age=42)
        Conversation.welcome_msg(instance)
