"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import logging

from rest_framework import permissions

from users.models import Conversation

logger = logging.getLogger(__name__)


class IsUserOwnerOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Object-level permission to allow only user-owners to edit it.
    Assumes the obj has a user-attribute
    """

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_anonymous:
            return False

        user = request.user
        bool_ = obj.user_id == user.id

        if not bool_:
            logger.warning(f"{user} is not the owner of the object {obj}")

        return bool_


class IsUserOwner(permissions.IsAuthenticated):
    """
    Object-level permission, which only allows owners of the object to access it
    """

    def has_object_permission(self, request, view, obj) -> bool:
        if request.user.is_anonymous:
            return False
        return obj.user_id == request.user.id


class IsInConversation(permissions.IsAuthenticated):
    """
    Allows only users who are participants in the conversation
    """

    def has_permission(self, request, view) -> bool:
        if not super().has_permission(request, view):
            return False

        id_ = view.kwargs.get("conversation_id")
        user_id = request.user.id
        in_conversation = Conversation.objects.filter(id=id_, users__in=[user_id]).exists()

        if not in_conversation:
            logger.warning(f"{request.user} is not in the conversation {id_}")

        return in_conversation
