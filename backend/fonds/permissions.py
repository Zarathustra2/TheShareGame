"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import logging

from rest_framework import permissions

from .models import Member

logger = logging.getLogger(__name__)


class IsFondLeaderOrReadOnly(permissions.IsAuthenticated):
    """
    Permission to allow only users who are also leader

    Requires a an url with an fond_id parameter
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        if user.is_anonymous:
            return False

        fond_id = view.kwargs.get("fond_id")
        is_leader = Member.objects.filter(fond_id=fond_id, user=user, leader=True).exists()
        return is_leader


class IsFondLeaderMemberOrDenied(permissions.IsAuthenticated):
    """
    Custom PermissionClass for to restrict a view to only fond leaders
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_anonymous:
            return False

        fond_id = view.kwargs.get("fond_id")
        is_leader = Member.objects.filter(fond_id=fond_id, user=user, leader=True).exists()

        if not is_leader:
            logger.info(f"{user} is not a leader of the fond with the id {fond_id}")

        return is_leader


class IsFondLeaderRequestUserOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Denies any user is not a fond leader

    Use this with caution since we only check if the user is a fond leader
    and not if the object(s) the user works with belong the fond of the user
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_anonymous:
            return False

        is_leader = Member.objects.filter(user=user, leader=True).exists()
        return is_leader


class IsInFond(permissions.IsAuthenticated):
    """
    Only Users who are member of the fond can access the view

    fond_id parameter in the url is required
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_anonymous:
            return False

        fond_id = view.kwargs.get("fond_id")
        in_fond = Member.objects.filter(fond_id=fond_id, user_id=user.id).exists()

        if not in_fond:
            logger.info(f"{user} is not in the fond with the id: {fond_id}")

        return in_fond
