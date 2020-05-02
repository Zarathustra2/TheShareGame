"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import logging

from django.db import transaction

from .models import FondProfile, Member, FondChatRoom

logger = logging.getLogger(__name__)


def delete_member(sender, instance, *args, **kwargs):
    """
    Pre-Delete-Signal for handling Members of a fond.

    If the member is also the founder of the fond we will assign one of
    the leaders to be the new founder automatically.

    If the member is the last member of the fond we will delete the fond as well.
    """

    member = instance
    user = member.user
    fond = member.fond

    fond_members = fond.member_set.all()

    logger.info(f"{member} is leaving the fond {fond}")

    if fond_members.count() == 0:
        logger.info("Last member of the fond, deleting the whole fond!")
        fond.delete()

    elif user == fond.founder:

        logger.info(f"{user} was the founder. Making another leader the founder")

        leaders = fond_members.filter(leader=True)
        try:
            leader = leaders[0]
            # founder is a user instance
            fond.founder = leader.user
        except IndexError:

            logger.info(f"No other leader in the fond, choosing another member as the new founder")

            # the fond does not have any leaders
            # so we assign the user who has been for the longest time in the fond the status leader & founder
            member = fond_members.order_by("-id").first()
            fond.founder = member.user
            member.leader = True
            member.save()

        fond.save()


def found_fond(sender, instance, created, *args, **kwargs):
    """
    Signal for founding a Fond

    Whenever a fond gets created, we also create the FondProfile as well as
    a Leader & Member-Model for the founding user
    """
    if created:
        fond = instance

        user = fond.founder

        logger.info(f"{fond} has been created. Creating models!")

        with transaction.atomic():
            Member.objects.create(user=user, fond=fond, leader=True)

            FondProfile.objects.create(fond=fond)
            FondChatRoom.objects.create(fond=fond, name=fond.name)
