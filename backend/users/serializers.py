"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import logging

from django.contrib.auth import authenticate
from rest_framework import serializers

from core.models import Company
from fonds.models import FondArticle, FondComment
from fonds.models import Member
from tsg.const import DATETIME_FORMAT
from tsg.settings import RECAPTCHA_SECRET_KEY
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
    UserComment,
    Profile,
)

import requests

logger = logging.getLogger(__name__)


class CreateUserSerializer(serializers.ModelSerializer):
    """
    Serializer used for registering a User
    """

    recaptcha_token = serializers.CharField(max_length=1000)

    class Meta:
        model = User
        fields = ("username", "password", "email", "recaptcha_token")
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ()

    def create(self, validated_data):

        data = {"secret": RECAPTCHA_SECRET_KEY, "response": validated_data.get("recaptcha_token")}

        rsp = requests.post("https://www.google.com/recaptcha/api/siteverify", json=data)
        if rsp.status_code != 200:
            raise serializers.ValidationError("Recaptcha did not succeed. Are you a robot?")

        user = User.objects.create_user(
            username=validated_data["username"], password=validated_data["password"], email=validated_data["email"]
        )

        logger.info(f"{user} has been created!")

        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for returning a User
    """

    class Meta:
        model = User
        fields = ("id", "username")
        read_only_fields = fields


class UserCompanyBvSerializer(serializers.ModelSerializer):
    """
    Serializer for a user, which also adds the total book value
    of the users' companies
    """

    class Meta:
        model = User
        fields = ("id", "username", "companies_book_value")
        read_only_fields = fields


class LoginUserSerializer(serializers.Serializer):
    """
    Serializer for logging in a User
    """

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])

        if user and user.is_active:
            return user

        # TODO: Add maximum of tries
        raise serializers.ValidationError("Either your username or your password is false.")

    def update(self, instance, validated_data):
        raise NotImplementedError

    def create(self, validated_data):
        raise NotImplementedError


class ConversationSerializer(serializers.ModelSerializer):
    users = UserSerializer(read_only=True, many=True)

    receivers_id = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    message_text = serializers.CharField(write_only=True)
    created = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)

    class Meta:
        model = Conversation
        fields = (
            "users",
            "unread_by",
            "subject",
            "created",
            "id",
            # write only
            "receivers_id",
            "message_text",
        )
        read_only_fields = ("unread_by", "users", "created")

    def create(self, validated_data):
        user = self.context["request"].user
        user_id = user.id

        subject = validated_data.get("subject")
        receivers = validated_data.get("receivers_id")
        txt = validated_data.get("message_text")

        obj = Conversation.create_new_conversation(receivers_id=receivers, subject=subject, sender_id=user_id)

        Message.objects.create(conversation_id=obj.id, text=txt, sender_id=user_id)

        return obj

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # we do not pass the request again over when accessing the Conversation over the messageListView
        if self.context.get("accessOverMessageList", False):
            return data

        user_id = self.context["request"].user.id

        # if user has not read the message yet, he will exist
        data["read"] = not instance.unread_by.filter(id=user_id).exists()

        return data

    def validate_receivers_id(self, value):
        user_id = self.context["request"].user.id
        if user_id in value:
            raise serializers.ValidationError("You cannot send messages to yourself")
        if len(value) > 10:
            raise serializers.ValidationError("You cannot start a conversation with more than 10 participants")
        if len(value) == 0:
            raise serializers.ValidationError("You need at least one receiver")
        return value


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    conversation_id = serializers.IntegerField(write_only=True)
    created = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)

    class Meta:
        model = Message
        fields = ("sender", "text", "created", "id", "conversation_id")
        read_only_fields = ("sender", "id", "created")

    def create(self, validated_data):
        user = self.context["request"].user
        user_id = user.id

        txt = validated_data.get("text")
        # Check if the user is a participant of the conversation
        # happens in the view via custom PermissionClass
        conversation_id = validated_data.get("conversation_id")

        obj = Message.create_new_message(conversation_id=conversation_id, text=txt, sender_id=user_id)

        return obj


class ArticleSerializer(serializers.ModelSerializer):
    fond_id = serializers.IntegerField(write_only=True, required=False)
    company_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Article
        fields = ("headline", "text", "created", "id", "company_id", "fond_id")
        read_only_fields = ("id", "created")

    def to_representation(self, instance):

        data = super().to_representation(instance)

        author = dict()

        # check whether the related-model exists
        if hasattr(instance, "companyarticle"):
            from core.serializers import CompanyUrlSerializer

            author = CompanyUrlSerializer(instance=instance.companyarticle.company).data

        elif hasattr(instance, "fondarticle"):
            from fonds.serializers import InvestmentFondUrlSerializer

            author = InvestmentFondUrlSerializer(instance=instance.fondarticle.fond).data

        data["author"] = author
        return data

    def create(self, validated_data):
        company_id = validated_data.get("company_id")
        fond_id = validated_data.get("fond_id")
        headline = validated_data.get("headline")
        text = validated_data.get("text")

        data = {"text": text, "headline": headline}

        if company_id:
            obj = CompanyArticle.objects.create(company_id=company_id, **data)
        elif fond_id:
            obj = FondArticle.objects.create(fond_id=fond_id, **data)
        else:
            raise ValueError("Neither an fond_id nor an company_id has been provided")

        return obj

    def validate_company_id(self, value):

        if value:
            user = self.context["request"].user
            user_id = user.id
            if Company.objects.filter(user_id=user_id, id=value).exists() is False:
                logger.warning(f"{user} is not the ceo of {value}!")
                raise serializers.ValidationError("You are not the ceo of this company")
        return value

    def validate_fond_id(self, value):

        # A fond_id is not requried as the posting company could as
        # write a company only for his company
        if value:
            user = self.context["request"].user
            user_id = user.id
            if Member.objects.filter(user_id=user_id, fond_id=value, leader=True).exists() is False:
                logger.warning(f"{user} is not a leader of the fond {value}")
                raise serializers.ValidationError("You are not a leader of the fond")
        return value

    def validate(self, attrs):
        company_id = attrs.get("company_id")
        fond_id = attrs.get("fond_id")

        if not (company_id or fond_id):
            logger.warning("Cannot create an article if neither a company_id, nor a fond_id is provided!")
            raise serializers.ValidationError({"fond_company_id": "You need to provide a company_id or fond_id"})
        return attrs


class CompanyArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyArticle
        fields = ("headline", "text", "created", "id")
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)

        from core.serializers import CompanyUrlSerializer

        author = CompanyUrlSerializer(instance=instance.company).data
        data["author"] = author

        return data


class CommentSerializer(serializers.ModelSerializer):
    is_fond_comment = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        model = Comment
        fields = ("text", "created", "article", "is_fond_comment")
        read_only_fields = ("created",)
        extra_kwargs = {"article": {"write_only": True}}

    def to_representation(self, instance):
        data = super().to_representation(instance)

        extras = dict()

        # check whether the related-model exists
        if hasattr(instance, "usercomment"):
            extras = UserSerializer(instance=instance.usercomment.user).data
        elif hasattr(instance, "fondcomment"):
            from fonds.serializers import InvestmentFondUrlSerializer

            extras = InvestmentFondUrlSerializer(instance=instance.fondcomment.fond).data

        data["author"] = extras
        return data

    def create(self, validated_data):
        text = validated_data.get("text")
        article = validated_data.get("article")
        fond = validated_data.get("is_fond_comment", False)
        _data = {"text": text, "article": article}

        user = self.context["request"].user
        if fond is False:
            obj = UserComment.objects.create(user=user, **_data)
        else:
            try:
                member = Member.objects.get(user=user)
            except Member.DoesNotExist:
                logger.warning(f"Cannot create FondComment as {user} is not in a fond!")
                raise serializers.ValidationError("You are not in a fond")

            obj = FondComment.objects.create(fond_id=member.fond_id, **_data)
        return obj

    def validate_text(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("You need to write at least 2 characters")
        return value

    def validate(self, attrs):
        fond = attrs.get("is_fond_comment", False)
        user = self.context["request"].user
        if fond:
            if Member.objects.filter(user=user).exists() is False:
                logger.warning(f"Cannot create FondComment as {user} is not in a fond!")
                raise serializers.ValidationError({"fond_comment": ["You are not in a fond"]})

        return attrs


class ThreadSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = ("name", "user", "slug", "created", "updated", "locked", "pinned", "id")
        read_only_fields = ("slug", "locked", "pinned", "created", "updated")

    def validate_name(self, value):
        if len(value) < 5:
            raise serializers.ValidationError(
                "Name of the Thread is too short. Name needs to be at least 5 characters long."
            )
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        name = validated_data.get("name")

        thread = Thread.objects.create(user=user, name=name)

        return thread


class ThreadPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    created = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)

    thread_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ThreadPost
        fields = ("user", "text", "created", "id", "thread_id")
        read_only_fields = ("user", "created", "id")

    def create(self, validated_data):
        user = self.context["request"].user
        text = validated_data.get("text")
        thread_id = validated_data.get("thread_id")

        thread_post = ThreadPost.objects.create(user=user, text=text, thread_id=thread_id)

        return thread_post

    def validate_thread_id(self, value):
        try:
            thread = Thread.objects.get(id=value)
        except Thread.DoesNotExist:
            logger.warning(f"Thread with the id {value} does not exist!")
            raise serializers.ValidationError("No Thread exists with the given id")

        # Only admins are allowed to post in a locked thread
        if thread.locked:
            user = self.context["request"].user
            if user.is_ingame_admin is False:
                logger.warning(f"{user} cannot lock a thread as he is not an admin!")
                raise serializers.ValidationError("You cannot post in a locked Thread")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)

    class Meta:
        model = Notification
        fields = ("text", "subject", "created", "id", "read")
        read_only_fields = fields


class ActiveUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")
        read_only_fields = fields


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    is_own_profile = serializers.BooleanField(default=False, read_only=True)

    class Meta:
        model = Profile
        fields = ("user", "description", "age", "is_own_profile", "company_logo")
        read_only_fields = ("user", "is_own_profile")

    def validate_company_logo(self, value):
        height, width = value.image.height, value.image.width

        err_msg = f"Logo must have a height of {Profile.IMAGE_H}px and a width of {Profile.IMAGE_W}px"

        if height != Profile.IMAGE_H:
            raise serializers.ValidationError(err_msg)

        if width != Profile.IMAGE_W:
            raise serializers.ValidationError(err_msg)

        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context["request"]
        user = request.user

        profile_user = data["user"]

        if user is not None and user.is_authenticated:
            data["is_own_profile"] = user.id == profile_user["id"]

        if profile_user is not None:
            from core.serializers import CompanyUrlSerializer

            company = dict()
            user = instance.user

            if hasattr(user, "company"):
                company = CompanyUrlSerializer(instance=instance.user.company).data
            data["company"] = company

        return data
