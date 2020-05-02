"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import random

from freezegun import freeze_time
from rest_framework.reverse import reverse

from common.test_base import NOW, NOW_FORMAT, NOW_STR, BaseTestCase
from fonds.models import InvestmentFond, Member
from users.models import (
    CompanyArticle,
    Conversation,
    Message,
    Notification,
    Thread,
    ThreadPost,
    User,
    UserComment,
    Article,
)


class UserApiTestCase(BaseTestCase):
    def test_registration_and_login(self):
        """Test the registration and login url"""
        url = reverse("users:register_user")
        client = self.client
        data = {
            "username": "JoeBottle",
            "password": "SuperSecret12",
            "email": "joe@bootle.com",
            "recaptcha_token": "TEST_TOKEN",
        }
        should_be_user_data = {"id": self.next_id(User), "username": "JoeBottle"}

        response = client.post(url, data=data)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(data.get("user"), should_be_user_data)
        self.assertTrue(data.get("token", False) is not False)

        # login-test

        data = {"username": "JoeBottle", "password": "SuperSecret12"}

        url = reverse("users:login")
        response = client.post(url, data)

        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data.get("token", False) is not False)

        data = {"username": "JoeBottle", "password": "WrongPassword"}

        url = reverse("users:login")
        response = client.post(url, data)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"non_field_errors": ["Either your username or your password is false."]})

    def test_user_lookup(self):
        joe = User.objects.create(username="joe_blocks", email="JoeBlocks@web.de")
        mustermann = User.objects.create(username="joe_mustermann", email="mustermann@web.de")

        url = reverse("users:users-lookup", kwargs={"name": "joe"})
        response = self.client.get(url)
        should_be = [{"id": joe.id, "username": "joe_blocks"}, {"id": mustermann.id, "username": "joe_mustermann"}]
        self.assertListEqual(response.json(), should_be)

        url = reverse("users:users-lookup", kwargs={"name": "blocks"})
        response = self.client.get(url)
        should_be = [{"id": joe.id, "username": "joe_blocks"}]
        self.assertListEqual(response.json(), should_be)

        url = reverse("users:users-lookup", kwargs={"name": "joe_m"})
        response = self.client.get(url)
        should_be = [{"id": mustermann.id, "username": "joe_mustermann"}]
        self.assertListEqual(response.json(), should_be)

    def test_user_retrieve(self):
        url = reverse("users:users-detail", kwargs={"id": self.user.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        should_be = {"id": self.user.id, "username": "A"}
        self.assertDictEqual(response.json(), should_be)


@freeze_time(NOW)
class ArticleApiTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.article = CompanyArticle.objects.create(
            company=self.company, headline="Headline", text="Text", accepted=True
        )

        self.article_not_accepted = CompanyArticle.objects.create(
            company=self.company, headline="NotAccepted", text="Text", accepted=False
        )

        self.comment = UserComment.objects.create(article=self.article, text="Commenting a Article", user=self.user_two)

        self.url = reverse("users:articles")

    def test_url(self):
        """Test the GET method of the newspaper page. Should return most
			recent articles"""
        url = self.url
        client = self.client
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_company_article(self):
        """Test the POST method of the newspaper page for creating articles"""
        user = self.user
        url = self.url
        client = self.client

        data = {"headline": "Headline", "text": "Some-Text", "company_id": user.company.id}
        next_id = self.next_id(Article)
        client.force_authenticate(user=user)

        response = client.post(url, data)
        self.assertEqual(response.status_code, 201)

        should_be = {
            "headline": "Headline",
            "text": "Some-Text",
            "created": NOW_STR,
            "id": next_id,
            "author": {"name": "Company", "user_id": user.id, "isin": self.company.isin, "id": self.company.id},
        }
        self.assertDictEqual(response.json(), should_be)

    def test_post_company_wrong_data(self):
        """Test POST method for the newspaper page with multiple corrupt
			data"""
        user = self.user_two
        url = self.url
        client = self.client

        # not ceo of the company
        data = {"headline": "Headline", "text": "Some-Text", "company_id": self.user.company.id}

        client.force_authenticate(user=user)
        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"company_id": ["You are not the ceo of this company"]})

    def test_post_no_id(self):
        user = self.user_two
        url = self.url
        client = self.client

        # not ceo of the company
        data = {"headline": "Headline", "text": "Some-Text"}

        client.force_authenticate(user=user)
        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"fond_company_id": ["You need to provide a company_id or fond_id"]})

    def test_no_data(self):
        user = self.user
        url = self.url
        client = self.client

        data = {"headline": "Headline", "text": "", "company_id": user.company.id}

        client.force_authenticate(user=user)
        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"text": ["This field may not be blank."]})

        data.update({"text": "text", "headline": ""})
        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"headline": ["This field may not be blank."]})

    def test_post_fond_article(self):
        """Test the POST method fo creating articles in the name of a fond"""
        user = self.user
        url = self.url
        client = self.client

        fond = InvestmentFond.objects.create(name="Fond", founder=user)
        data = {"headline": "Headline", "text": "Some-Text", "fond_id": fond.id}

        next_id = self.next_id(Article)
        client.force_authenticate(user=user)
        response = client.post(url, data)
        self.assertEqual(response.status_code, 201)
        should_be = {
            "headline": "Headline",
            "text": "Some-Text",
            "created": NOW_STR,
            "id": next_id,
            "author": {"name": "Fond", "id": fond.id, "slug": "fond"},
        }
        self.assertDictEqual(response.json(), should_be)

        # not the leader of the fond
        not_leader = self.user_two
        Member.objects.create(user=not_leader, fond=fond)
        client.force_authenticate(user=not_leader)
        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"fond_id": ["You are not a leader of the fond"]})

    def test_company_article_url(self):
        """
			Test the GET method for the company_articles page
			Should return all articles of a company
			"""

        isin = self.company.isin
        url = reverse("users:articles_company", kwargs={"isin": isin})

        client = self.client
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        should_be = [
            {
                "headline": "Headline",
                "text": "Text",
                "created": NOW_STR,
                "id": self.article.id,
                "author": {"name": "Company", "user_id": self.user.id, "isin": isin, "id": self.company.id},
            },
        ]
        result = response.json().get("results")

        self.assertListEqual(result, should_be)

    def test_get_comments(self):
        """
			Test the GET method of the comments url
			Should return all comments of the given article
			"""
        url = reverse("users:article_comments", kwargs={"article_id": self.article.id})
        client = self.client

        response = client.get(url)

        self.assertEqual(response.status_code, 200)

        should_be = [
            {"text": "Commenting a Article", "created": NOW_STR, "author": {"id": self.user_two.id, "username": "D"}}
        ]
        self.assertListEqual(response.json(), should_be)

    def test_post_user_comments(self):
        """Test the POST method for the comments_url"""
        url = reverse("users:article_comments", kwargs={"article_id": self.article.id})
        client = self.client

        article_id = self.article.id
        data = {"text": "A Comment", "article": article_id}
        client.force_authenticate(user=None)
        response = client.post(url, data)
        self.assertEqual(response.status_code, 401)

        client.force_authenticate(user=self.user)
        response = client.post(url, data)
        self.assertEqual(response.status_code, 201)

        should_be = {"text": "A Comment", "created": NOW_STR, "author": {"id": self.user.id, "username": "A"}}
        self.assertDictEqual(response.json(), should_be)

        data = {"text": "a", "article": article_id}
        response = client.post(url, data)

        self.assertEqual(response.status_code, 400)
        should_be = {"text": ["You need to write at least 2 characters"]}
        self.assertDictEqual(response.json(), should_be)

    def test_post_fond_comment(self):
        """Test that comments can be written in the name of a fond"""
        url = reverse("users:article_comments", kwargs={"article_id": self.article.id})
        user = self.user
        client = self.client
        fond = InvestmentFond.objects.create(founder=user, name="A")

        data = {"text": "Fond", "is_fond_comment": True, "article": self.article.id}
        client.force_authenticate(user=user)
        response = client.post(url, data)

        self.assertEqual(response.status_code, 201)

        should_be = {"text": "Fond", "created": NOW_STR, "author": {"name": "A", "id": fond.id, "slug": "a"}}
        self.assertDictEqual(response.json(), should_be)

        # does not have a fond
        user_two = self.user_two
        client.force_authenticate(user=user_two)
        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"fond_comment": ["You are not in a fond"]})


@freeze_time(NOW)
class ThreadApiTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("users:threads")
        self.thread = Thread.objects.create(user=self.user, name="ThreadTestCase")

    def test_url(self):
        """Test the GET method of the forum page, returns threads"""
        url = self.url
        client = self.client

        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json().get("results")[0]

        should_be = {
            "name": "ThreadTestCase",
            "user": {"id": self.user.id, "username": "A"},
            "slug": "threadtestcase",
            "created": NOW_STR,
            "updated": NOW_STR,
            "locked": False,
            "pinned": False,
            "id": self.thread.id,
        }

        self.assertDictEqual(should_be, data)

    def test_thread_creation(self):
        """Test the POST method of the forum page for creating a thread"""
        user = self.user
        url = self.url
        client = self.client

        data = {"name": "A New Thread"}
        should_be = {
            "name": "A New Thread",
            "user": {"id": user.id, "username": "A"},
            "slug": "a-new-thread",
            "created": NOW_STR,
            "updated": NOW_STR,
            "locked": False,
            "pinned": False,
            "id": self.next_id(Thread),
        }

        client.force_authenticate(user=user)
        response = client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(should_be, response.json())

        data = {"name": "1"}
        response = client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, 400)
        should_be = {"name": ["Name of the Thread is too short. Name needs to be at least 5 characters long."]}
        self.assertDictEqual(response.json(), should_be)

    def test_thread_creation_anonymous(self):
        """Test that anonymous users cannot create a thread"""
        url = self.url
        client = self.client
        data = {"name": "A New Thread"}
        client.force_authenticate(user=None)
        response = client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 401)


@freeze_time(NOW)
class ThreadPostApiTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.thread = Thread.objects.create(user=self.user, name="Thread")
        self.post = ThreadPost.objects.create(user=self.user, thread_id=self.thread.id, text="This is a Post")

        self.url = reverse("users:thread_posts", kwargs={"thread_id": self.thread.id})
        self.delete_update_url = reverse(
            "users:thread_post_destroy_update", kwargs={"thread_id": self.thread.id, "post_id": self.post.id}
        )

    def test_url(self):
        """Test the GET method for a single thread"""
        url = self.url
        client = self.client
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_creation(self):
        """Test users can post in a thread"""
        url = self.url
        user = self.user
        client = self.client

        data = {"text": "another post", "thread_id": self.thread.id}
        should_be = {
            "user": {"id": user.id, "username": "A"},
            "text": "another post",
            "created": NOW_FORMAT,
            "id": self.next_id(ThreadPost),
        }

        client.force_authenticate(user)
        response = client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(response.json(), should_be)

    def test_deleting_post(self):
        """Test users can deleted their posts"""

        url = self.delete_update_url
        user = self.user
        client = self.client
        before = ThreadPost.objects.count()
        client.force_authenticate(user)
        response = client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(ThreadPost.objects.count(), before - 1)

        # Create a new post which belong to user
        obj = ThreadPost.objects.create(user=self.user, thread_id=self.thread.id, text="This should not be deleted")
        client.force_authenticate(self.user_two)

        before = ThreadPost.objects.count()

        url = reverse("users:thread_post_destroy_update", kwargs={"thread_id": obj.thread.id, "post_id": obj.id})
        client.delete(url)

        self.assertTrue(ThreadPost.objects.filter(id=obj.id).exists())
        self.assertEqual(before, ThreadPost.objects.count())

    def test_updating_post(self):
        """Test users can update their posts"""
        url = self.delete_update_url
        user = self.user
        client = self.client

        data = {"text": "Update", "thread_id": self.thread.id}
        should_be = {
            "user": {"id": user.id, "username": "A"},
            "text": "Update",
            "created": NOW_FORMAT,
            "id": self.post.id,
        }

        client.force_authenticate(user)

        response = client.put(url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), should_be)

        client.force_authenticate(user=self.user_two)
        response = client.put(url, data)
        self.assertEqual(response.status_code, 403)

    def test_post_thread_locked(self):
        """Test non admin users cannot post in a locked thread"""
        url = self.url
        user = self.user_two
        client = self.client

        thread = Thread.objects.create(user=self.user, name="Locked", locked=True)

        data = {"text": "breaking in", "thread_id": thread.id}

        client.force_authenticate(user)
        response = client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"thread_id": ["You cannot post in a locked Thread"]})
        self.assertEqual(ThreadPost.objects.filter(thread_id=thread.id).count(), 0)


@freeze_time(NOW)
class ConversationApiTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.third_user = User.objects.create(username="Mr.3", email="mrThree@web.de")
        self.conversation = Conversation.objects.create(subject="HelloWorld")
        self.msg = Message.objects.create(conversation=self.conversation, sender=self.user, text="Hey whats up?")
        self.conversation.users.add(self.user, self.user_two)
        self.conversation.unread_by.add(self.user_two)

    def test_get_url(self):
        """Test the GET method of the Conversations url"""
        url = reverse("users:conversations")
        client = self.client

        client.force_authenticate(user=None)
        response = client.get(url)
        self.assertEqual(response.status_code, 401)

        user = self.user
        client.force_authenticate(user=user)

        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        should_be = [
            {
                "users": [{"id": self.user.id, "username": "A"}, {"id": self.user_two.id, "username": "D"}],
                "unread_by": [self.user_two.id],
                "subject": "HelloWorld",
                "created": NOW_FORMAT,
                "id": self.conversation.id,
                "read": True,
            }
        ]
        data = response.json().get("results")
        self.assertListEqual(data, should_be)

    def test_post_url(self):
        """Test the POST method for creating a new Conversation"""
        url = reverse("users:conversations")
        user = self.user
        client = self.client
        receivers_id = [self.user_two.id, self.third_user.id]
        message_text = "Hey, How are You?"
        subject = "Hey"

        data = {"receivers_id": receivers_id, "message_text": message_text, "subject": subject}

        client.force_authenticate(user=user)
        response = client.post(url, data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.user_two.conversations_unread.count(), 2)
        self.assertEqual(self.third_user.conversations_unread.count(), 1)
        self.assertEqual(self.user.conversations_unread.count(), 0)

        self.assertEqual(self.user.conversations.count(), 2)
        self.assertEqual(self.user_two.conversations.count(), 2)
        self.assertEqual(self.third_user.conversations.count(), 1)

    def test_false_data(self):
        """Test the POST method with multiple corrupt data"""
        url = reverse("users:conversations")
        user = self.user
        client = self.client
        message_text = "Hey, How are You?"
        subject = "Hey"

        data = {"receivers_id": [], "message_text": message_text, "subject": subject}

        client.force_authenticate(user=user)

        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"receivers_id": ["This field is required."]})

        data.update({"receivers_id": 2, "message_text": ""})
        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"message_text": ["This field may not be blank."]})

        data.update({"subject": "", "message_text": "A"})
        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"subject": ["This field may not be blank."]})

        data.update({"subject": "A", "message_text": "A", "receivers_id": self.user.id})
        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"receivers_id": ["You cannot send messages to yourself"]})

        list_ = list()
        while len(list_) <= 10:
            x = self.user.id
            while x in list_ or x == self.user.id:
                x = random.randint(1, 1000)
            list_.append(x)
        data.update({"receivers_id": list_})
        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.json(), {"receivers_id": ["You cannot start a conversation with more than 10 participants"]}
        )

    def test_create_new_message(self):
        """Test the create_new_message method for creating a new message in
			a Conversation"""
        conversation = self.conversation
        sender = self.user_two

        Message.create_new_message(conversation_id=conversation.id, text="Received your message", sender_id=sender.id)

        # tests update_read_by
        self.assertEqual(sender.conversations_unread.count(), 0)
        self.assertEqual(self.user.conversations_unread.count(), 1)

    def test_get_message(self):
        """
			Test the GET method of a single conversation
			Should return the all messages of the conversation
		"""
        url = reverse("users:messages", kwargs={"conversation_id": self.conversation.id})
        user = self.user
        client = self.client

        client.force_authenticate(user=None)
        response = client.get(url)
        self.assertEqual(response.status_code, 401)

        client.force_authenticate(user=self.third_user)
        response = client.get(url)
        self.assertEqual(response.status_code, 403)

        client.force_authenticate(user=user)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        should_be = [
            {
                "sender": {"id": self.user.id, "username": "A"},
                "text": "Hey whats up?",
                "created": NOW_FORMAT,
                "id": self.msg.id,
            }
        ]
        self.assertEqual(response.json().get("results"), should_be)

    def test_post_message(self):
        """Test the POST method for creating a new message in a Conversation"""
        url = reverse("users:messages", kwargs={"conversation_id": self.conversation.id})
        user = self.user_two
        client = self.client

        data = {"conversation_id": self.conversation.id, "text": "I said hi back"}

        client.force_authenticate(user=self.third_user)
        response = client.post(url, data)
        self.assertEqual(response.status_code, 403)

        client.force_authenticate(user=user)
        response = client.post(url, data)
        self.assertEqual(response.status_code, 201)

        should_be = {
            "conversation": {
                "created": NOW_FORMAT,
                "id": self.conversation.id,
                "subject": "HelloWorld",
                "unread_by": [self.user.id],
                "users": [{"id": self.user.id, "username": "A"}, {"id": user.id, "username": "D"}],
            },
            "sender": {"id": user.id, "username": "D"},
            "text": "I said hi back",
            "created": NOW_FORMAT,
            "id": Message.objects.latest("id").id,
        }
        self.assertEqual(response.json(), should_be)

        # tests update_read_by
        self.assertEqual(user.conversations_unread.count(), 0)
        self.assertEqual(self.user.conversations_unread.count(), 1)

    def test_not_participant_of_conversation(self):
        """Test that users cannot send message to conversations where they are not in the list of receivers"""
        url = reverse("users:messages", kwargs={"conversation_id": 1})
        user = self.third_user
        client = self.client

        data = {"conversation_id": 1, "text": "Should not work"}

        client.force_authenticate(user=user)
        response = client.post(url, data)

        self.assertEqual(response.status_code, 403)


@freeze_time(NOW)
class NotificationApiTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.notification_one = Notification.objects.create(user=self.user, text="Notification1", subject="subject")

        self.notification_two = Notification.objects.create(user=self.user_two, text="Notification2", subject="subject")
        self.fond = InvestmentFond.objects.create(founder=self.user, name="Fond")

        self.url = reverse("users:notifications")

    def test_notifications(self):
        """Test the GET method for Notifications page """
        url = self.url
        user = self.user
        client = self.client
        client.force_authenticate(user=user)

        response = client.get(url)

        self.assertEqual(response.status_code, 200)

        should_be = [
            {
                "text": "Notification1",
                "subject": "subject",
                "created": NOW_FORMAT,
                "id": self.notification_one.id,
                "read": False,
            },
        ]

        data = response.json().get("results")
        self.assertListEqual(data, should_be)

    def test_single_notification_retrieve(self):
        """
        Test that the retrieve get method for a single notifications works
        If it has not been read yet, it should update
        """

        url = reverse("users:notification", kwargs={"id": self.notification_one.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

        self.client.force_authenticate(user=self.user)
        self.assertFalse(Notification.objects.get(id=self.notification_one.id).read)

        with self.assertNumQueries(2):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        should_be = {
            "text": "Notification1",
            "subject": "subject",
            "created": NOW_FORMAT,
            "id": self.notification_one.id,
            "read": True,
        }
        self.assertDictEqual(response.json(), should_be)

        self.assertTrue(Notification.objects.get(id=self.notification_one.id).read)

        url = reverse("users:notification", kwargs={"id": 10000})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        url = reverse("users:notification", kwargs={"id": self.notification_two.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


class UnreadApiTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        Notification.objects.create(user=self.user, text="Notification1", subject="Subject1")
        Notification.objects.create(user=self.user, text="Notification1", subject="Subject1")
        Notification.objects.create(user=self.user, text="Notification1", subject="Subject1", read=True)

        self.unread_notifications = 2

        self.conversation = Conversation.objects.create(subject="HelloWorld")
        self.msg = Message.objects.create(conversation=self.conversation, sender=self.user, text="Hey whats up?")
        self.conversation.users.add(self.user, self.user_two)
        self.conversation.unread_by.add(self.user_two)

        self.url = reverse("users:unread")

    def test_unread(self):
        client = self.client
        client.force_authenticate(user=self.user)
        rsp = client.get(self.url)

        self.assertDictEqual(rsp.json(), {"unread_messages": 0, "unread_notifications": 2})

    def test_unread_unread_conversation(self):
        client = self.client
        client.force_authenticate(user=self.user_two)
        rsp = client.get(self.url)

        self.assertDictEqual(rsp.json(), {"unread_messages": 1, "unread_notifications": 0})

    def test_unread_not_authenticated(self):
        url = reverse("users:unread")
        self.client.force_authenticate(user=None)
        rsp = self.client.get(url)
        self.assertEqual(rsp.status_code, 400)


class ActiveUserApiTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("users:active_user")

    def test_own_user_data(self):
        self.client.force_authenticate(user=self.user)
        rsp = self.client.get(self.url)
        should_be = {"id": self.user.id, "username": self.user.username}
        self.assertDictEqual(should_be, rsp.json())

    def test_not_authenticated(self):
        self.client.force_authenticate(user=None)
        rsp = self.client.get(self.url)

        self.assertEqual(401, rsp.status_code)


class ProfileApiTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("users:profile", kwargs={"id": self.user.id})

    def test_retrieve(self):
        self.client.force_authenticate(user=None)
        rsp = self.client.get(self.url)

        c = self.user.company

        rsp_json = rsp.json()
        self.assertIsNotNone(rsp_json.get("company_logo", None))

        # I don't know hwo to compute the url for the iamge field
        # during testing. So I just that that the field has been set and then delete it from
        # the response to assert the dict.
        del rsp_json["company_logo"]

        should_be = {
            "user": {"id": self.user.id, "username": self.user.username},
            "description": "This user prefers to keep an air of mystery about them.",
            "age": 42,
            "company": {"id": c.id, "isin": c.isin, "name": c.name, "user_id": self.user.id},
            "is_own_profile": False,
        }

        self.assertEqual(200, rsp.status_code)
        self.assertDictEqual(should_be, rsp_json)

    def test_is_own_profile(self):
        self.client.force_authenticate(user=self.user)
        rsp = self.client.get(self.url)
        is_own_profile = rsp.json().get("is_own_profile")
        self.assertTrue(is_own_profile)

    def test_is_own_profile_other_user(self):
        self.client.force_authenticate(user=self.user_two)
        rsp = self.client.get(self.url)
        is_own_profile = rsp.json().get("is_own_profile")
        self.assertFalse(is_own_profile)

    def test_can_update_own_profile(self):
        self.client.force_authenticate(user=self.user)
        data = {"age": 99, "description": "Lorem Ipsum"}
        rsp = self.client.put(self.url, data)

        self.user.profile.refresh_from_db()
        self.assertEqual(200, rsp.status_code)
        self.assertEqual(data.get("age"), self.user.profile.age)
        self.assertEqual(data.get("description"), self.user.profile.description)

    def test_cannot_update_profile_of_other_user(self):
        self.client.force_authenticate(user=self.user_two)
        data = {"age": 99, "description": "Lorem Ipsum"}

        profile_before = self.user.profile

        rsp = self.client.put(self.url, data)
        self.assertEqual(403, rsp.status_code)

        self.user.profile.refresh_from_db()
        self.assertEqual(profile_before.age, self.user.profile.age)
        self.assertEqual(profile_before.description, self.user.profile.description)

    def test_cannot_update_user(self):
        self.client.force_authenticate(user=self.user)
        data = {"user": {"username": "New-Name"}}
        rsp = self.client.put(self.url, data, format="json")
        self.assertEqual(400, rsp.status_code)

        data = {"user_id": 2}
        rsp = self.client.put(self.url, data, format="json")
        self.assertEqual(400, rsp.status_code)
