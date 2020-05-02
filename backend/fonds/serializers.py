"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import logging

from rest_framework import serializers

from fonds.models import FondApplication, FondProfile, FondThread, InvestmentFond, Member, FondThreadPost
from tsg.const import DATETIME_FORMAT
from users.serializers import ThreadSerializer, UserCompanyBvSerializer, UserSerializer

logger = logging.getLogger(__name__)


class FondProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FondProfile
        fields = ("description", "open_for_application", "id", "logo")
        read_only_fields = ("id",)


class InvestmentFondSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)
    profile = FondProfileSerializer(source="fondprofile", read_only=True)

    class Meta:
        model = InvestmentFond
        fields = ("name", "id", "amount_members", "slug", "created", "profile")
        read_only_fields = ("id", "amount_members", "slug", "created", "profile")

    def create(self, validated_data):
        name = validated_data.get("name")

        user = self.context["request"].user
        obj = InvestmentFond.objects.create(founder=user, name=name)
        return obj

    def validate(self, attrs):
        user = self.context["request"].user

        if user.has_fond:
            logger.warning(f"{user} is already in a fond, cannot found new fond")
            raise serializers.ValidationError("You are already in a Fond")
        return attrs


class InvestmentFondUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentFond
        fields = ("name", "id", "slug")
        read_only_fields = fields


class MemberSerializer(serializers.ModelSerializer):
    user = UserCompanyBvSerializer()

    class Meta:
        model = Member
        fields = ("user", "leader", "id")
        read_only_fields = fields


class InvestmentFondDetailsSerializer(serializers.ModelSerializer):
    members = MemberSerializer(source="member_set", many=True)
    profile = FondProfileSerializer(source="fondprofile")
    created = serializers.DateTimeField(format=DATETIME_FORMAT)
    founder = UserSerializer()

    class Meta:
        model = InvestmentFond
        fields = ("name", "id", "members", "profile", "created", "founder")
        read_only_fields = fields


class FondApplicationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    created = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)

    fond_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FondApplication
        fields = (
            "id",
            "user",
            "text",
            "created",
            # Write Only
            "fond_id",
        )
        read_only_fields = ("user", "created", "id")

    def validate_text(self, value):
        """Validate that the text has at least a length of 50"""
        if len(value) < 50:
            raise serializers.ValidationError("You need to ride at least 50 chars")
        return value

    def validate_fond_id(self, value):
        """Validate that the user does not have another open application for this fond"""
        user_id = self.context["request"].user.id
        other_application_exists = FondApplication.objects.filter(user_id=user_id, fond_id=value)

        if other_application_exists:
            logger.warning(f"{user_id} tried to apply again to {value}")
            raise serializers.ValidationError(
                "You cannot apply again while you have a fond application for the same fond"
            )
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        user_id = user.id
        fond_id = validated_data.get("fond_id")

        text = validated_data.get("text")

        obj = FondApplication.objects.create(user_id=user_id, fond_id=fond_id, text=text)
        logger.info(f"{user} applied to {fond_id}")
        return obj


class UserFondDataSerializer(serializers.ModelSerializer):
    fond = InvestmentFondUrlSerializer()

    class Meta:
        model = Member

        fields = ("fond", "leader", "id")
        read_only_fields = fields


class InvestmentFondProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FondProfile
        fields = ("description", "open_for_application", "id", "logo")
        read_only_fields = ("id",)


class FondThreadSerializer(ThreadSerializer):
    class Meta:
        model = FondThread
        fields = ("name", "user", "slug", "created", "updated", "locked", "pinned", "id")
        read_only_fields = ("slug", "locked", "pinned")

    def create(self, validated_data):
        user = self.context["request"].user
        name = self.validated_data.get("name")
        fond_id = self.context["fond_id"]

        assert Member.objects.filter(user_id=user.id, fond_id=fond_id).exists()

        return FondThread.objects.create(user_id=user.id, name=name, fond_id=fond_id)


class FondThreadPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    created = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)

    class Meta:
        model = FondThreadPost
        fields = ("user", "text", "created", "id")
        read_only_fields = ("user", "created", "id")

    def create(self, validated_data):
        user = self.context["request"].user
        text = validated_data.get("text")
        thread_id = self.context["thread_id"]

        thread_fond_id = FondThread.objects.only("id").get(id=thread_id).fond_id
        assert Member.objects.filter(fond_id=thread_fond_id, user=user).exists()

        thread_post = FondThreadPost.objects.create(user=user, text=text, thread_id=thread_id,)

        return thread_post
