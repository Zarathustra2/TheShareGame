"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import logging

from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import (
    DestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    UpdateAPIView,
    get_object_or_404,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from common.pagination import StandardResultsSetPagination
from common.views import BaseListAPIServerSide
from core.models import Company
from users.models import (
    Article,
    Comment,
    CompanyArticle,
    Conversation,
    Message,
    Notification,
    Thread,
    ThreadPost,
    User,
    Profile,
)
from users.permissions import IsInConversation, IsUserOwnerOrReadOnly, IsUserOwner
from users.serializers import (
    ArticleSerializer,
    CommentSerializer,
    ConversationSerializer,
    CreateUserSerializer,
    LoginUserSerializer,
    MessageSerializer,
    NotificationSerializer,
    ThreadPostSerializer,
    ThreadSerializer,
    UserSerializer,
    ActiveUserSerializer,
    ProfileSerializer,
    CompanyArticleSerializer,
)


logger = logging.getLogger(__name__)


class RegistrationAPI(generics.GenericAPIView):
    """
	View for creating a new User and returning the User as well as his/her API-Token
	"""

    serializer_class = CreateUserSerializer
    renderer_classes = (JSONRenderer,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"user": UserSerializer(user, context=self.get_serializer_context()).data, "token": user.get_token()}
        )


class LoginAPI(generics.GenericAPIView):
    """
	View for logging in a User
	"""

    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response(
            {"user": UserSerializer(user, context=self.get_serializer_context()).data, "token": user.get_token()}
        )


class ArticleListCreateAPIView(BaseListAPIServerSide, ListCreateAPIView):
    """
	get:
	Returns a list of Articles ordered by id

	post:
	Create a new Article
	"""

    serializer_class = ArticleSerializer
    queryset = Article.objects.filter(accepted=True).select_related(
        "companyarticle", "fondarticle", "companyarticle__company", "fondarticle__fond"
    )
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)


class ArticleCompanyListAPIView(BaseListAPIServerSide, ListAPIView):
    """
	Returns a list of Articles by a company ordered by DateTime
	"""

    serializer_class = CompanyArticleSerializer
    pagination_class = StandardResultsSetPagination
    queryset = CompanyArticle.objects.select_related("company").all()

    def get_filter_kwargs(self):
        isin = self.kwargs.get("isin")
        id_ = Company.get_id_from_isin(isin)
        return {"accepted": True, "company_id": id_}


class ThreadListCreateAPIView(BaseListAPIServerSide, ListCreateAPIView):
    """
	get:
	Returns a list of all threads of the country ordered by pinned and id

	post:
	Create a new Thread
	"""

    serializer_class = ThreadSerializer
    queryset = Thread.objects.select_related("user").all()
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    default_ordering = ["pinned", "-id"]


class ThreadPostListCreateAPIView(BaseListAPIServerSide, ListCreateAPIView):
    """
	get:
	Returns a list of posts for a thread ordered by date time

	post:
	Create a new Post
	"""

    queryset = ThreadPost.objects.select_related("user").all()
    serializer_class = ThreadPostSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_filter_kwargs(self):
        thread_id = self.kwargs.get("thread_id")

        return {"thread_id": thread_id}


class ThreadPostDestroyUpdateView(DestroyAPIView, UpdateAPIView):
    """
	delete:
	Deletes a post in the forum

	put:
	Updates a post in the forum
	"""

    serializer_class = ThreadPostSerializer
    permission_classes = (IsUserOwnerOrReadOnly,)

    def get_object(self):
        filter_ = self.get_filter_kwargs()
        obj = get_object_or_404(ThreadPost, **filter_)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_filter_kwargs(self):
        dict_ = dict()
        dict_["id"] = self.kwargs.get("post_id")
        return dict_

    def destroy(self, request, *args, **kwargs):
        ThreadPost.objects.filter(**self.get_filter_kwargs(), user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        obj = self.get_object()
        data = request.data
        # TODO: LOL
        data["thread_slug"] = "fix-this-hack"

        serializer = ThreadPostSerializer(obj, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConversationListCreateAPIView(BaseListAPIServerSide, ListCreateAPIView):
    """
	get:
	Return all conversations of a user

	post:
	Create a new conversation
	"""

    serializer_class = ConversationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthenticated,)
    queryset = Conversation.objects.prefetch_related("users", "unread_by").all()

    def get_filter_kwargs(self):
        user_id = self.request.user.id
        return {"users__in": [user_id]}


class MessageJsonRenderer(JSONRenderer):
    """
    Custom Renderer for the MessagesListCreateAPIView which also adds information about
    the conversation
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        kwargs = renderer_context.get("kwargs")
        id_ = kwargs.get("conversation_id")
        if id_:
            try:
                obj = Conversation.objects.prefetch_related("users").get(id=id_)
                data["conversation"] = ConversationSerializer(obj, context={"accessOverMessageList": True}).data
            except Conversation.DoesNotExist:
                pass

        return super().render(data, accepted_media_type, renderer_context)


class MessagesListCreateAPIView(BaseListAPIServerSide, ListCreateAPIView):
    """
	get:
	Get all messages of a conversation

	post:
	Create a new message
	"""

    serializer_class = MessageSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsInConversation,)
    renderer_classes = (MessageJsonRenderer,)
    queryset = Message.objects.select_related("sender").all()

    def get_filter_kwargs(self):
        id_ = self.kwargs.get("conversation_id")
        return {"conversation_id": id_}

    def get(self, request, *args, **kwargs):
        rsp = super().get(request, args, kwargs)

        # User has opened the message, so we delete him from the unread list
        c = Conversation.objects.get(id=self.kwargs.get("conversation_id"))
        c.unread_by.remove(self.request.user.id)

        return rsp


class NotificationListAPIView(BaseListAPIServerSide, ListAPIView):
    """
	Returns the notifications of the user
	"""

    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination

    def get_filter_kwargs(self):
        user_id = self.request.user.id
        return {"user_id": user_id}


class NotificationRetrieveView(RetrieveAPIView):
    serializer_class = NotificationSerializer
    permission_classes = (IsUserOwner,)

    def get_object(self):
        obj = get_object_or_404(Notification.objects, id=self.kwargs["id"])
        self.check_object_permissions(self.request, obj)
        if obj.read is False:
            Notification.objects.filter(id=obj.id).update(read=True)
            obj.read = True
        return obj


class CommentListCreateAPIView(ListCreateAPIView):
    """
	get:
	Returns all comments for the given article

	post:
	Creates a new comment
	"""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        article_id = self.kwargs.get("article_id")
        qs = Comment.objects.select_related("usercomment", "fondcomment").filter(article_id=article_id)
        return qs


class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    lookup_field = "id"

    def get_object(self):
        return get_object_or_404(User, id=self.kwargs["id"])

    @action(detail=False, methods=["get"], url_path="lookup/(?P<name>[-\w]+)")
    def lookup(self, request, name=None):
        qs = User.objects.filter(username__icontains=name)
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)


class UnreadRetrieveView(RetrieveAPIView):
    """
    Returns the unread messages and notifications of the user
    """

    def get(self, request, *args, **kwargs):
        request = self.request
        user = request.user
        data = dict()

        if user.is_anonymous:
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        data["unread_messages"] = Conversation.objects.filter(unread_by__in=[user.id]).count()
        data["unread_notifications"] = Notification.objects.filter(user_id=user.id, read=False).count()
        return Response(data=data)


class ActiveUserRetrieveView(RetrieveAPIView):
    """
    Returns of the data of the authenticated user
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ActiveUserSerializer

    def get_object(self):
        return self.request.user


class ProfileRetrieveUpdateView(RetrieveUpdateAPIView):
    """
    Returns the profile for a given user
    """

    serializer_class = ProfileSerializer
    permission_classes = (IsUserOwnerOrReadOnly,)

    def get_object(self):
        user_id = self.kwargs.get("id")
        try:
            profile = Profile.objects.get(user_id=user_id)
            self.check_object_permissions(self.request, profile)
            return profile
        except Profile.DoesNotExist:
            logger.exception(f"{user_id} does not have a profile")
            return None
