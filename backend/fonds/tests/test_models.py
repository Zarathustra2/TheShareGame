from django.db import IntegrityError

from common.test_base import BaseTestCase
from fonds.models import Member, InvestmentFond, FondProfile, FondApplication
from users.models import User


class FondTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.fond = InvestmentFond.objects.create(founder=self.user, name="Fond")
        self.member = Member.objects.create(user=self.user_two, fond=self.fond)

    def test_str(self):
        self.assertEqual("Fond", str(self.fond))

    def test_amount_members(self):
        self.assertEqual(self.fond.amount_members(), 2)

    def test_slug_unicode(self):
        self.assertEqual("fond", self.fond.slug)

        # Delete the user_tow from the fond, so he can found a new fond
        self.user_two.member.delete()
        chinese_fond = InvestmentFond.objects.create(founder=self.user_two, name="影師嗎")

        self.assertEqual(chinese_fond.slug, "ying-shi-ma")

    def test_datetime_gets_set(self):
        self.assertIsNotNone(self.fond.created)

    def test_cannot_found_fond_if_in_fond(self):
        with self.assertRaises(IntegrityError):
            InvestmentFond.objects.create(founder=self.user_two, name="Error")

    def test_delete_signal_no_other_leader(self):
        """
        Test that when the only fond leader deletes a fond the member
        who has been the longest time in the fond will become the new leader & founder
        """

        fond = self.fond
        user = User.objects.create(username="Q", email="Q@web.de")
        user_two = User.objects.create(username="W", email="W@web.de")
        Member.objects.bulk_create([Member(user=user, fond=fond), Member(user=user_two, fond=fond)])

        Member.objects.filter(user=self.user, fond=fond).delete()

        new_leader = Member.objects.filter(fond=fond).order_by("-id").first()

        self.refresh_from_db(fond)
        self.assertEqual(fond.founder, new_leader.user)

    def test_delete_signal_other_leader(self):
        """
        Test the deletion of the fond by the founder. Another leader will become the new founder
        """

        fond = self.fond
        user = User.objects.create(username="Q", email="Q@web.de")
        user_two = User.objects.create(username="W", email="W@web.de")
        Member.objects.bulk_create([Member(user=user, fond=fond, leader=True), Member(user=user_two, fond=fond)])

        Member.objects.filter(user=self.user, fond=fond).delete()

        self.refresh_from_db(fond)
        self.assertEqual(fond.founder, user)


class MemberTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.fond = InvestmentFond.objects.create(founder=self.user, name="Fond")

    def test_member_delete(self):
        """
        Test when the only member which is ultimately also the founder & leader
        gets deleted that also the fond gets deleted
        """
        id_ = self.fond.id
        self.user.member.delete()
        self.assertFalse(InvestmentFond.objects.filter(id=id_).exists())

    def test_user_deleted_also_deletes_member(self):
        self.user.delete()
        self.assertEqual(Member.objects.count(), 0)

    def test_fond_deleted_also_deletes_member(self):
        self.fond.delete()
        self.assertEqual(Member.objects.count(), 0)

    def test_leader_default_false(self):
        m = Member.objects.create(user=self.user_two, fond=self.fond)
        self.assertFalse(m.leader)

    def test_str(self):
        self.assertEqual(str(self.user.member), "A Fond")


class FondProfileTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.fond = InvestmentFond.objects.create(founder=self.user, name="Fond")
        self.profile = self.fond.fondprofile

    def test_str(self):
        self.assertEqual(str(self.profile), str(self.fond))

    def test_only_one_profile_per_fond(self):
        with self.assertRaises(IntegrityError):
            FondProfile.objects.create(fond=self.fond)

    def test_fond_deleted_also_deletes_profile(self):
        self.fond.delete()
        self.assertEqual(FondProfile.objects.count(), 0)


class FondApplicationTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.fond = InvestmentFond.objects.create(founder=self.user, name="Fond")
        self.user_three = User.objects.create(username="Three", email="Three@web.de")
        self.fond_two = InvestmentFond.objects.create(founder=self.user_three)
        self.application = FondApplication.objects.create(fond=self.fond, user=self.user_two, text="invite me")

    def test_can_also_apply_at_other_fonds(self):
        FondApplication.objects.create(fond=self.fond_two, user=self.user_two, text="invite me")
        self.assertEqual(FondApplication.objects.filter(user=self.user_two).count(), 2)

    def test_cannot_apply_multiple_times_at_the_same_fond(self):
        with self.assertRaises(IntegrityError):
            FondApplication.objects.create(fond=self.fond, user=self.user_two, text="invite me")

    def test_user_deleted_also_deletes_application(self):
        self.assertEqual(FondApplication.objects.count(), 1)
        self.user_two.delete()
        self.assertEqual(FondApplication.objects.count(), 0)

    def test_fond_deleted_also_deletes_application(self):
        self.assertEqual(FondApplication.objects.count(), 1)
        self.fond.delete()
        self.assertEqual(FondApplication.objects.count(), 0)
