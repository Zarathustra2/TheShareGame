"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from freezegun import freeze_time
from rest_framework.reverse import reverse

from common.test_base import NOW, NOW_FORMAT, NOW_STR, BaseTestCase
from fonds.models import (
    FondApplication,
    FondProfile,
    FondThread,
    InvestmentFond,
    Member,
    FondChatRoom,
    FondThreadPost,
)
from fonds.serializers import FondProfileSerializer
from tsg.const import DATETIME_FORMAT
from users.models import User, Thread


@freeze_time(NOW)
class FondApiTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.fond = InvestmentFond.objects.create(founder=self.user, name="Fond")
        self.member = Member.objects.create(user=self.user_two, fond=self.fond)
        self.url = reverse("fonds:fonds")

    def test_list_url(self):
        """Test the listview of the fonds"""
        url = reverse("fonds:fonds")
        client = self.client
        response = client.get(url)
        # ToDo: Test Body
        self.assertEqual(response.status_code, 200)

    def test_detail_url(self):
        """Test the site for a single fond"""
        url = reverse("fonds:fond", kwargs={"fond_id": self.fond.id})
        client = self.client
        response = client.get(url)
        # ToDo: Test Body
        self.assertEqual(response.status_code, 200)

    def test_creation_signal(self):
        """
        Test that on creation of a fond by a user corresponding
        member with leader status gets created as well as a profile for the fond
        """
        self.assertTrue(Member.objects.filter(user=self.user, fond=self.fond).exists())

        self.assertTrue(FondProfile.objects.filter(fond=self.fond).exists())

        member = Member.objects.get(user=self.user)

        self.assertTrue(Member.objects.filter(id=member.id, leader=True).exists())

        self.assertTrue(FondChatRoom.objects.filter(fond=self.fond).exists())

    def test_fond_creation(self):
        """Test that a user without a fond can create a new one"""
        url = reverse("fonds:fonds")
        client = self.client

        data = {"name": "new fond"}

        client.force_authenticate(user=self.company.user)
        response = client.post(url, data)

        self.assertEqual(response.status_code, 400)

        user = User.objects.create(username="WithoutFond", email="WithoutFond@web.de")

        client.force_authenticate(user=user)

        response = client.post(url, data)

        self.assertEqual(201, response.status_code)
        self.assertEqual(data.get("name"), response.json().get("name"))

    def test_fond_profile_can_retrieve_data(self):
        """Test that fond leaders can update the profile"""
        url = reverse("fonds:fond_profile", kwargs={"fond_id": self.fond.id})
        client = self.client

        client.force_authenticate(user=None)

        response = client.get(url)

        self.assertEqual(response.status_code, 200)
        should_be = {"description": "Description of the Fond", "open_for_application": True, "id": self.fond.id}

        rsp_json = response.json()
        self.assertIsNotNone(rsp_json.get("logo", None))

        del rsp_json["logo"]

        self.assertDictEqual(should_be, rsp_json)

    def test_none_auth_user_cannot_update_profile(self):
        url = reverse("fonds:fond_profile", kwargs={"fond_id": self.fond.id})
        data = {"description": "No Applications anymore!", "open_for_application": False}

        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 401)

    def test_none_leader_cannot_update_profile(self):
        url = reverse("fonds:fond_profile", kwargs={"fond_id": self.fond.id})
        data = {"description": "No Applications anymore!", "open_for_application": False}

        # member of the fond but not a leader
        self.client.force_authenticate(user=self.user_two)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 403)

    def test_leader_can_upate_profile(self):
        url = reverse("fonds:fond_profile", kwargs={"fond_id": self.fond.id})
        data = {"description": "No Applications anymore!", "open_for_application": False}

        self.client.force_authenticate(user=self.user)

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, 200)

        data.update({"id": self.fond.id})

        rsp_json = response.json()
        del rsp_json["logo"]
        self.assertDictEqual(data, rsp_json)

    def test_fond_retrieve_slim_view(self):
        url = reverse("fonds:fond_slim", kwargs={"fond_id": self.fond.id})
        rsp = self.client.get(url)
        self.assertEqual(200, rsp.status_code)


@freeze_time(NOW)
class MemberApiTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.fond = InvestmentFond.objects.create(founder=self.user, name="Fond")

    def test_user_fond_data(self):
        """Test the retrieve of the users fond data"""
        url = reverse("fonds:user_fond_data")
        client = self.client

        client.force_authenticate(user=None)
        response = client.get(url)
        self.assertEqual(response.status_code, 401)

        user = User.objects.create(username="R", email="R@web.de")
        client.force_authenticate(user=user)
        response = client.get(url)
        self.assertEqual(response.status_code, 404)

        user = self.user
        client.force_authenticate(user=user)
        response = client.get(url)

        should_be = {
            "fond": {"name": "Fond", "id": self.fond.id, "slug": "fond",},
            "leader": True,
            "id": self.fond.member_set.first().id,
        }

        rsp_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), should_be)

    def test_user_leave_fond(self):
        """Test that users can leave a fond"""
        url = reverse("fonds:user_fond_data")
        client = self.client

        client.force_authenticate(user=None)
        response = client.get(url)
        self.assertEqual(response.status_code, 401)

        user = self.user
        client.force_authenticate(user=user)
        response = client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Member.objects.filter(user=user).count(), 0)

        # fond should be deleted as well since in this case
        # the test user was the only member of the fond
        self.assertEqual(InvestmentFond.objects.filter(founder=user).count(), 0)


@freeze_time(NOW)
class ApplicationApiTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.fond = InvestmentFond.objects.create(founder=self.user, name="Fond")

        self.user_two = User.objects.create(username="ABC", email="ABC@web.de")

        self.user_not_leader = self.user_not_leader = User.objects.create(
            username="NotALeader", email="NOtALeader@web.de"
        )
        Member.objects.create(user=self.user_not_leader, fond=self.fond)

        self.application = FondApplication.objects.create(fond=self.fond, user=self.user_two, text="invite me")

        self.url = reverse("fonds:fonds")

        self.url_application = reverse(
            "fonds:application_destroy", kwargs={"fond_id": self.fond.id, "application_id": self.application.id}
        )

        self.user_three = User.objects.create(username="Three", email="Three@gmail.com")

    def test_application_view(self):
        """Test that only fond leaders can view applications"""
        url = reverse("fonds:applications", kwargs={"fond_id": self.fond.id})
        client = self.client

        # not authenticated
        client.force_authenticate(user=None)
        response = client.get(url)
        self.assertEqual(response.status_code, 404)

        # not a fond leader
        client.force_authenticate(user=self.user_two)
        response = client.get(url)
        self.assertEqual(response.status_code, 404)

        # fond leaders, so access granted
        client.force_authenticate(user=self.user)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_fond_application(self):
        """Test that users can apply to a fond"""

        user = User.objects.create(username="WithoutFond", email="WithoutFond@web.de")
        fond_id = self.fond.id
        url = reverse("fonds:applications", kwargs={"fond_id": fond_id})
        client = self.client
        client.force_authenticate(user=user)

        data = {"fond_id": fond_id, "text": "A" * 50}
        should_be = {
            "user": {"id": user.id, "username": "WithoutFond"},
            "text": "A" * 50,
            "created": NOW_FORMAT,
            "id": self.next_id(FondApplication),
        }

        response = client.post(url, data)

        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(should_be, response.json())

        # sending another application to the same fond
        # should fail
        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)
        should_be = {"fond_id": ["You cannot apply again while you have a fond application for the same fond"]}
        self.assertDictEqual(response.json(), should_be)

    def test_application_text__too_short(self):
        """Test that applications by users fail if the text is too short"""

        user = User.objects.create(username="WithoutFond", email="WithoutFond@web.de")
        url = reverse("fonds:applications", kwargs={"fond_id": 1})
        client = self.client
        client.force_authenticate(user=user)

        data = {"fond_id": 1, "text": "A"}

        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)

        should_be = {"text": ["You need to ride at least 50 chars"]}
        self.assertDictEqual(response.json(), should_be)

    def test_none_leaders_cannot_accept_application(self):
        self.client.force_authenticate(user=self.user_not_leader)
        response = self.client.delete(self.url_application, data={"accepted": True})
        self.assertEqual(response.status_code, 403)

    def test_accept_application(self):
        """Test that fond leaders can accept applications"""
        leader = self.user
        self.client.force_authenticate(user=leader)
        response = self.client.delete(self.url_application, data={"accepted": True})

        self.assertEqual(response.status_code, 204)
        self.assertEqual(FondApplication.objects.filter(id=self.application.id).count(), 0)
        self.assertTrue(Member.objects.filter(fond=self.fond, user=self.application.user).exists())

    def test_none_leaders_cannot_decline_application(self):
        self.client.force_authenticate(user=self.user_not_leader)
        response = self.client.delete(self.url_application, data={"accepted": False}, json="json")

        self.assertEqual(response.status_code, 403)

    def test_decline_application(self):
        """Test that fond leaders can decline applications"""

        leader = self.user
        self.client.force_authenticate(user=leader)
        response = self.client.delete(self.url_application, data={"accepted": False}, format="json")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(FondApplication.objects.filter(id=self.application.id).count(), 0)
        self.assertFalse(Member.objects.filter(fond=self.fond, user=self.application.user).exists())

    def test_if_application_gets_accepted_others_get_deleted_of_the_user(self):
        fond_snd = InvestmentFond.objects.create(name="Three", founder=self.user_three)
        FondApplication.objects.create(fond=fond_snd, user=self.user_two, text="invite me")

        self.assertEqual(2, FondApplication.objects.filter(user=self.user_two).count())

        # Accept the other application
        self.test_accept_application()

        self.assertEqual(0, FondApplication.objects.filter(user=self.user_two).count())


@freeze_time(NOW)
class FondThreadApiTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.fond = InvestmentFond.objects.create(founder=self.user, name="Fond")

        self.fond_two = InvestmentFond.objects.create(founder=self.user_two, name="FondTwo")

        self.fond_thread = FondThread.objects.create(fond=self.fond, user=self.user, name="Simple Thread")
        self.fond_two_thread = FondThread.objects.create(fond=self.fond_two, user=self.user_two, name="Simple Thread")
        self.url = reverse("fonds:forum", kwargs={"fond_id": self.fond.id})

    def test_url(self):
        """Test the GET method that the right threads get returned for a user"""

        url = self.url
        client = self.client

        client.force_authenticate(user=None)
        response = client.get(url)
        self.assertEqual(response.status_code, 401)

        client.force_authenticate(user=self.user_two)
        response = client.get(url)
        self.assertEqual(response.status_code, 403)

        client.force_authenticate(user=self.user)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        should_be = [
            {
                "name": "Simple Thread",
                "user": {"id": self.user.id, "username": "A"},
                "slug": "simple-thread",
                "created": NOW_STR,
                "updated": NOW_STR,
                "locked": False,
                "pinned": False,
                "id": self.fond_thread.id,
            }
        ]
        self.assertListEqual(response.json().get("results"), should_be)

    def test_thread_creation(self):
        """Test the POST method of the fond forum page for creating a thread"""

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
            "id": self.next_id(FondThread),
        }

        client.force_authenticate(user=self.user_two)
        response = client.post(url, data)
        self.assertEqual(response.status_code, 403)

        client.force_authenticate(user=user)
        response = client.post(url, data)
        self.assertEqual(response.status_code, 201)

        self.assertDictEqual(should_be, response.json())

        data = {"name": "1"}
        response = client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, 400)
        should_be = {"name": ["Name of the Thread is too short. Name needs to be at least 5 characters long."]}
        self.assertDictEqual(response.json(), should_be)


@freeze_time(NOW)
class FondThreadPostApiTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.fond = InvestmentFond.objects.create(founder=self.user, name="Fond")
        self.member = Member.objects.create(user=self.user_two, fond=self.fond)

        self.user_three = User.objects.create(username="Three", email="Three@web.de")
        self.other_fond = InvestmentFond.objects.create(founder=self.user_three, name="Other-Fond")

        self.fond_thread = FondThread.objects.create(fond=self.fond, name="Thread")

        self.fond_thread_post = FondThreadPost.objects.create(
            thread_id=self.fond_thread.id, text="Lorem Ipsum norem.", user=self.user
        )

        self.url = reverse("fonds:thread", kwargs={"fond_id": self.fond.id, "thread_id": self.fond_thread.id})

    def test_retrieve_data(self):
        self.client.force_authenticate(user=self.user)
        rsp = self.client.get(self.url)
        self.assertEqual(200, rsp.status_code)

    def test_cannot_access_if_not_authenticated(self):
        self.client.force_authenticate(user=None)
        rsp = self.client.get(self.url)
        self.assertEqual(401, rsp.status_code)

    def test_cannot_access_if_not_in_same_fond(self):
        self.client.force_authenticate(user=self.user_three)
        rsp = self.client.get(self.url)
        self.assertEqual(403, rsp.status_code)

    def test_can_create_new_post(self):
        data = {"text": "This is a post"}
        self.client.force_authenticate(user=self.user)

        rsp = self.client.post(self.url, data)

        self.assertEqual(201, rsp.status_code)
        self.assertEqual(2, FondThreadPost.objects.filter(thread_id=self.fond_thread.id).count())

    def test_cannot_create_new_post_if_not_authenticated(self):
        data = {"text": "This is a post"}
        self.client.force_authenticate(user=None)

        rsp = self.client.post(self.url, data)

        self.assertEqual(401, rsp.status_code)
        self.assertEqual(1, FondThreadPost.objects.filter(thread_id=self.fond_thread.id).count())

    def test_cannot_create_new_post_if_not_in_same_fond(self):
        data = {"text": "This is a post"}
        self.client.force_authenticate(user=self.user_three)

        rsp = self.client.post(self.url, data)

        self.assertEqual(403, rsp.status_code)
        self.assertEqual(1, FondThreadPost.objects.filter(thread_id=self.fond_thread.id).count())


class UserFondApiTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.fond = InvestmentFond.objects.create(name="Fond", founder=self.user)
        Member.objects.create(fond=self.fond, user=self.user_two)

        self.url = reverse("fonds:user_fond_data")

        self.user_three = User.objects.create(username="Three", email="Three@gmail.com")

    def test_retrieve_fond_data_anonymous(self):
        self.client.force_authenticate(user=None)

        rsp = self.client.get(self.url)
        self.assertEqual(401, rsp.status_code)

    def test_retrieve_fond_data_no_fond(self):
        self.client.force_authenticate(user=self.user_three)

        rsp = self.client.get(self.url)
        self.assertEqual(404, rsp.status_code)

    def test_retrieve_fond_data_leader(self):
        self.client.force_authenticate(user=self.user)

        rsp = self.client.get(self.url)
        self.assertEqual(200, rsp.status_code)

        rsp_json = rsp.json()
        self.assertEqual(self.fond.name, rsp_json.get("fond").get("name"))
        self.assertTrue(rsp_json.get("leader"))

    def test_retrieve_fond_data_none_leader(self):
        self.client.force_authenticate(user=self.user_two)

        rsp = self.client.get(self.url)
        self.assertEqual(200, rsp.status_code)

        rsp_json = rsp.json()
        self.assertEqual(self.fond.name, rsp_json.get("fond").get("name"))
        self.assertFalse(rsp_json.get("leader"))

    def test_fond_leave_anonymous(self):
        self.client.force_authenticate(user=None)
        rsp = self.client.delete(self.url)
        self.assertEqual(401, rsp.status_code)

    def test_fond_leave_no_fond(self):
        self.client.force_authenticate(user=self.user_three)
        rsp = self.client.delete(self.url)
        self.assertEqual(404, rsp.status_code)

    def test_fond_leave_leader(self):
        self.client.force_authenticate(user=self.user)

        rsp = self.client.delete(self.url)

        self.assertEqual(204, rsp.status_code)
        self.assertFalse(Member.objects.filter(user=self.user, fond=self.fond).exists())
        self.assertTrue(InvestmentFond.objects.filter(id=self.fond.id).exists())
        self.assertTrue(Member.objects.filter(user=self.user_two, leader=True).exists())

    def test_fond_leave_none_leader(self):
        self.client.force_authenticate(user=self.user_two)

        rsp = self.client.delete(self.url)

        self.assertEqual(204, rsp.status_code)
        self.assertFalse(Member.objects.filter(user=self.user_two, fond=self.fond).exists())
        self.assertTrue(InvestmentFond.objects.filter(id=self.fond.id).exists())

    def test_fond_leave_last_member(self):
        Member.objects.filter(fond=self.fond).exclude(user=self.user).delete()

        self.client.force_authenticate(user=self.user)
        rsp = self.client.delete(self.url)
        self.assertEqual(204, rsp.status_code)
        self.assertFalse(InvestmentFond.objects.filter(id=self.fond.id).exists())
