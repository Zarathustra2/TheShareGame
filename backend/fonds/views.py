"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import logging
from distutils.util import strtobool

from rest_framework import status
from rest_framework.generics import (
    DestroyAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveDestroyAPIView,
    RetrieveUpdateAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from common.pagination import StandardResultsSetPagination
from common.views import BaseListAPIServerSide
from .models import FondApplication, FondProfile, FondThread, InvestmentFond, Member, FondThreadPost
from .permissions import IsFondLeaderMemberOrDenied, IsFondLeaderOrReadOnly, IsFondLeaderRequestUserOrReadOnly, IsInFond
from .serializers import (
    FondApplicationSerializer,
    FondThreadSerializer,
    InvestmentFondDetailsSerializer,
    InvestmentFondProfileSerializer,
    InvestmentFondSerializer,
    UserFondDataSerializer,
    FondThreadPostSerializer,
    InvestmentFondUrlSerializer,
)

logger = logging.getLogger(__name__)


class InvestmentFondAPICreateListView(BaseListAPIServerSide, ListCreateAPIView):
    """
    get:
    Returns all InvestmentFonds

    post:
    Creates an new InvestmentFond
    """

    serializer_class = InvestmentFondSerializer
    queryset = InvestmentFond.objects.select_related("fondprofile").all()
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class InvestmentFondRetrieveAPIView(RetrieveAPIView):
    """
    Returns a fond
    """

    serializer_class = InvestmentFondDetailsSerializer

    def get_object(self):
        id = self.kwargs.get("fond_id")
        return get_object_or_404(
            InvestmentFond.objects.prefetch_related("member_set", "member_set__user__company").select_related(
                "fondprofile", "founder"
            ),
            id=id,
        )


class InvestmentFondSlimRetrieveAPIView(RetrieveAPIView):
    serializer_class = InvestmentFondUrlSerializer

    def get_object(self):
        id = self.kwargs.get("fond_id")
        return get_object_or_404(InvestmentFond, id=id)


class FondApplicationCreateListView(BaseListAPIServerSide, ListCreateAPIView):
    """

    get:
    Returns all applications for a fond. User must be a fond-leader
    to view applications

    post:
    Create new fond application
    """

    serializer_class = FondApplicationSerializer
    pagination_class = StandardResultsSetPagination
    default_ordering = "-id"
    queryset = FondApplication.objects.all()

    def get_filter_kwargs(self):
        fond_id = self.get_fond_id()
        return {"fond_id": fond_id}

    def get_fond_id(self):
        user = self.request.user
        obj = get_object_or_404(Member, user=user, leader=True)
        return obj.fond_id


class FondApplicationDestroyView(DestroyAPIView):
    """
    Accept/Decline an application and delete it.
    Can only be accessed by a fond leader
    """

    permission_classes = (IsFondLeaderRequestUserOrReadOnly,)

    def get_object(self):
        id_ = self.kwargs.get("application_id")
        fond_id = self.request.user.member.fond_id
        obj = get_object_or_404(FondApplication, fond_id=fond_id, id=id_)
        return obj

    def delete(self, request, *args, **kwargs):

        obj = self.get_object()
        accepted = self.request.data.get("accepted")

        user = self.request.user

        if accepted:
            logger.info(f"{user} has accepted the application of {obj.user}")
            obj.accept_application(leader_user=user)
        else:
            logger.info(f"{user} has declined the application of {obj.user}")
            obj.decline_application()

        # Delete all remaining applications of the user as he has joined
        # a fond now.
        FondApplication.objects.filter(user=obj.user).all().delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserFondRetrieveView(RetrieveDestroyAPIView):
    """
    get:
    Returns the fond data of a user

    delete:
    Removes the user from the fond
    """

    serializer_class = UserFondDataSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        user = self.request.user
        return get_object_or_404(Member.objects.select_related("fond"), user=user)

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()

        assert obj.user_id == request.user.id
        obj.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class FondProfileUpdateRetrieveView(RetrieveUpdateAPIView):
    """
    get:
    Returns the profile of a fond given by slug

    put:
    Updates the profile of a fond given by a slug. User needs to be a leader
    """

    serializer_class = InvestmentFondProfileSerializer
    permission_classes = (IsFondLeaderOrReadOnly,)

    def get_object(self):
        fond_id = self.kwargs.get("fond_id")
        obj = get_object_or_404(FondProfile, fond_id=fond_id)
        return obj


class FondThreadListCreateAPIView(BaseListAPIServerSide, ListCreateAPIView):
    """
    get:
    Returns a list of all threads of the fond ordered by pinned and last updated

    post:
    Create a new Thread
    """

    serializer_class = FondThreadSerializer
    queryset = FondThread.objects.all()
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsInFond,)
    default_ordering = ["pinned", "-updated"]

    def get_filter_kwargs(self):
        fond_id = self.kwargs.get("fond_id")
        return {"fond_id": fond_id}

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["fond_id"] = self.kwargs.get("fond_id")
        return ctx


class FondThreadPostListCreateAPIView(BaseListAPIServerSide, ListCreateAPIView):
    queryset = FondThreadPost.objects.all()
    serializer_class = FondThreadPostSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsInFond,)

    def get_filter_kwargs(self):
        thread_id = self.kwargs.get("thread_id")
        return {"thread_id": thread_id}

    def get_object(self):
        obj = super().get_object()
        if not Member.objects.filter(user=self.request.user, fond_id=obj.thread.id).exists():
            raise PermissionError
        return obj

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["thread_id"] = self.kwargs.get("thread_id")
        return ctx
