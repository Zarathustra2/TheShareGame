"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from django.db import transaction
from django.db.utils import IntegrityError
from rest_framework.authtoken.models import Token

from common.test_base import BaseTestCase
from core.models import PrivateDepot
from fonds.models import InvestmentFond
from users.models import (
    User,
    CompanyArticle,
    UserComment,
    Thread,
    ThreadPost,
    Message,
    Conversation,
    Notification,
    Profile,
)


class UserTestCase(BaseTestCase):
    def test_user_have_unique_usernames(self):
        User.objects.all().delete()
        User.objects.create(username="Max", email="M@web.de")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create(username="Max", email="M2@web.de")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create(username="max", email="M2@web.de")

    def test_users_have_an_api_token(self):
        self.assertTrue(Token.objects.filter(user=self.user).exists())

    def test_has_fond(self):
        user = self.user
        self.assertFalse(user.has_fond)

        InvestmentFond.objects.create(founder=user, name="A")

        # Clear the cached property
        # The property is only cached for the duration of the request
        del user.__dict__["has_fond"]
        self.assertTrue(user.has_fond)

    def test_private_depot_exists(self):
        self.assertTrue(PrivateDepot.objects.filter(user=self.user).exists())

    def test_email_field_unique(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create(username="max", email=self.user.email)

    def test_users_have_an_profile(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())


class ArticleTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.article = CompanyArticle.objects.create(
            company=self.company, headline="Headline", text="Text", accepted=True
        )

        self.comment = UserComment.objects.create(article=self.article, text="Commenting a Article", user=self.user_two)

    def test_str(self):
        self.assertEqual(str(self.article), self.article.headline)

    def test_slug(self):
        chinese_article = CompanyArticle.objects.create(company=self.company, headline="#影師嗎", text="#影師嗎")

        self.assertEqual(chinese_article.slug, "ying-shi-ma")
        self.assertEqual(chinese_article.text, "#影師嗎")

        self.article_not_accepted = CompanyArticle.objects.create(
            company=self.company, headline="NotAccepted", text="Text", accepted=False
        )

    def test_headline_automatically_as_slug(self):
        self.assertEqual("headline", self.article.slug)

    def test_created_gets_set(self):
        self.assertIsNotNone(self.article.created)

    def test_if_company_gets_deleted_then_also_article(self):
        self.article.company.delete()
        self.assertEqual(0, CompanyArticle.objects.count())


class UserCommentTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.article = CompanyArticle.objects.create(
            company=self.company, headline="Headline", text="Text", accepted=True
        )

        self.comment = UserComment.objects.create(article=self.article, text="Commenting a Article", user=self.user_two)

    def test_comment_exists_after_user_deleted(self):
        self.comment.user.delete()
        self.assertTrue(UserComment.objects.filter(id=self.comment.id).exists())
        self.assertIsNone(UserComment.objects.get(id=self.comment.id).user)

    def test_comment_deleted_after_article_deleted(self):
        self.article.delete()
        self.assertEqual(0, UserComment.objects.count())

    def test_created_gets_set(self):
        self.assertIsNotNone(self.comment.created)


class ThreadTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.thread = Thread.objects.create(user=self.user, name="ThreadTestCase")

    def test_str(self):
        self.assertEqual(str(self.thread), self.thread.name)

    def test_slug_unicode(self):
        chinese_thread = Thread.objects.create(user=self.user, name="#影師嗎")
        self.assertEqual(chinese_thread.slug, "ying-shi-ma")

    def test_thread_exists_after_user_deleted(self):
        self.thread.user.delete()
        self.assertTrue(Thread.objects.filter(id=self.thread.id).exists())

    def test_created_gets_set(self):
        self.assertIsNotNone(self.thread.created)

    def test_locked_and_pinned_default_off(self):
        self.assertFalse(self.thread.pinned)
        self.assertFalse(self.thread.locked)


class ThreadPostTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.thread = Thread.objects.create(user=self.user, name="Thread")
        self.post = ThreadPost.objects.create(user=self.user, thread_id=self.thread.id, text="This is a Post")

    def test_threadposts_deleted_after_thread_deleted(self):
        self.thread.delete()
        self.assertEqual(0, ThreadPost.objects.count())

    def test_thread_cannot_be_null(self):
        with self.assertRaises(IntegrityError):
            ThreadPost.objects.create(user=self.user, text="Lorem Ipsum")


class ConversationTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.third_user = User.objects.create(username="Mr.3")
        self.conversation = Conversation.objects.create(subject="HelloWorld")
        self.conversation.users.add(self.user, self.user_two)
        self.conversation.unread_by.add(self.user_two)
        Message.objects.create(conversation=self.conversation, sender=self.user, text="Hey whats up?")

    def test_str(self):
        self.assertEqual(str(self.conversation), self.conversation.subject)

    def test_create_new_conversation(self):
        receivers = [self.user_two.id, self.third_user.id]
        sender_id = self.user.id
        Conversation.create_new_conversation(receivers_id=receivers, sender_id=sender_id, subject="Abc")

        self.assertEqual(self.user_two.conversations_unread.count(), 2)
        self.assertEqual(self.third_user.conversations_unread.count(), 1)
        self.assertEqual(self.user.conversations_unread.count(), 0)

        self.assertEqual(self.user.conversations.count(), 2)
        self.assertEqual(self.user_two.conversations.count(), 2)
        self.assertEqual(self.third_user.conversations.count(), 1)

    def test_conversation_exists_if_user_gets_deleted(self):
        self.user.delete()
        self.assertTrue(Conversation.objects.filter(id=self.conversation.id).exists())

    def test_welcome_msg_django_exists(self):
        django = User.objects.create(username="django", email="django@web.de")
        Conversation.welcome_msg(self.user)

        self.assertTrue(Conversation.objects.filter(users__in=[django.id, self.user.id]).exists())

    def test_welcome_does_not_fail_if_django_does_not_exist(self):
        self.assertFalse(User.objects.filter(username="django").exists())
        Conversation.objects.filter(users__in=[self.user.id]).delete()
        Conversation.welcome_msg(self.user)
        self.assertFalse(Conversation.objects.filter(users__in=[self.user.id]).exists())


class NotificationTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.notification = Notification.objects.create(user=self.user, text="Notification", subject="subject")
        self.fond = InvestmentFond.objects.create(founder=self.user, name="Fond")

    def test_str(self):
        self.assertEqual(self.fond.name, str(self.fond))
