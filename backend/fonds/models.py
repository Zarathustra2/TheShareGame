"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from __future__ import annotations
from django.db import models
from django.template.defaultfilters import slugify
from rest_framework.reverse import reverse
from unidecode import unidecode

from common.storage import OverwriteStorage
from common.utils import MarkdownText
from notify.events import Event, store_event
from users.models import BaseThread, BaseThreadPost, Article, Comment, ChatRoom, Notification


class InvestmentFond(models.Model):
    """
    InvestmentFond are groups of players. Each fonds has an own forum and chat
    only accessible by the players of the fonds.

    Players can also only be a member of one fond at a time.

    The purpose of a fond is that players can discuss strategies with each
    other or help each other to invest better.

    Users can found a new InvestmentFond
    """

    # Null allowed since players can leave the game but we still want to keep
    # the investment-fond
    founder = models.OneToOneField("users.User", on_delete=models.SET_NULL, null=True)

    name = models.CharField(max_length=25, unique=True)

    slug = models.SlugField(blank=False, null=False)

    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        db_table = "fond"

    def amount_members(self) -> int:
        """Returns the amount of members in the fond, ToDo: Save as field in db instead of query?"""
        return self.member_set.count()

    def save(self, *args, **kwargs):
        if not self.slug or kwargs.pop("updated_name", False):
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Member(models.Model):
    """
    Represents a fond-membership of a user
    """

    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    fond = models.ForeignKey(InvestmentFond, on_delete=models.CASCADE)

    # If the user is a leader in the fond
    # fond leaders have special rights and can delete/close forum threads
    # invite members and more
    leader = models.BooleanField(default=False)

    class Meta:
        db_table = "fond_member"

    def __str__(self):
        return f"{self.user} {self.fond}"


def upload_location(instance, filename):
    _, extension = filename.split(".")
    name = instance.fond.name
    name = name.replace(" ", "_")
    return "fond_logo/%s.%s" % (name, extension)


class FondProfile(models.Model):
    """
    Model for storing profiles of a Fond

    Profiles contain information about the description and if they are
    open for applications

    """

    fond = models.OneToOneField(InvestmentFond, on_delete=models.CASCADE)

    description = models.TextField(default="Description of the Fond")

    # If set to true, the fond accepts application from
    # other users
    open_for_application = models.BooleanField(default=True)

    # The logo of the fond
    logo = models.ImageField(upload_to=upload_location, default="logo_default.jpg", storage=OverwriteStorage())

    class Meta:
        db_table = "fond_profile"

    def __str__(self):
        return str(self.fond)


class FondApplication(models.Model):
    """
    Model for storing Applications of users for a fond
    """

    fond = models.ForeignKey(InvestmentFond, on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    text = models.TextField()

    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        # Users can only have one active application for a fond
        unique_together = ("fond", "user")
        db_table = "fond_application"

    def __str__(self):
        return f"{self.user} {self.fond}"

    def accept_application(self, leader_user) -> None:
        """
        Accepts an application and adds the user to the fond.

        Furthermore, everyone in the fond will get a notification that a new member
        has been added to the fond.
        """

        subject = f"Welcome to {self.fond}"

        text = (
            f"Your application has been accepted. You have joined {self.fond}\n\n"
            f"Best regards, {leader_user} - {self.fond}"
        )

        Member.objects.create(user_id=self.user_id, fond=self.fond)

        notifications = []
        for member in self.fond.member_set.all():
            notifications.append(
                Notification(
                    user_id=member.user_id,
                    text=f"Welcome {self.user} in your fond!",
                    subject=f"{self.user} joined {self.fond}",
                )
            )
        notifications.append(Notification(user=self.user, subject=subject, text=text))

        notifications = Notification.objects.bulk_create(notifications)

        for obj in notifications:
            e = Event(user_id=obj.user_id, typ="Notification", msg=obj.subject)
            store_event(e)

    def decline_application(self) -> Notification:
        """Declines the applications and sends a notification to the user"""

        subject = f"Application Declined"
        text = f"Your application has been declined. Best Regards, {self.fond}"

        return Notification.objects.create(user=self.user, subject=subject, text=text)


class FondThread(BaseThread):
    """
    Model for storing the Threads of a fond

    See BaseThread for a detailed explanation how a forum works.
    """

    fond = models.ForeignKey(InvestmentFond, on_delete=models.CASCADE)

    # Reverse accessor clash
    read_by = models.ManyToManyField("users.User", related_name="read_fond_threads")

    class Meta:
        db_table = "fond_thread"


class FondThreadPost(BaseThreadPost):
    """
    Model for storing Posts of a FondThread

    See BaseThreadPost for a detailed explanation how a thread works.
    """

    thread = models.ForeignKey(FondThread, on_delete=models.CASCADE, null=False)

    class Meta:
        db_table = "fond_thread_post"


class FondArticle(Article):
    """
    Model for Articles written by a Fond

    See Article for detailed explanation how articles work.
    """

    fond = models.ForeignKey("fonds.InvestmentFond", on_delete=models.CASCADE)

    class Meta:
        db_table = "fond_article"


class FondComment(Comment):
    """Model to store Fond-Comments"""

    fond = models.ForeignKey("fonds.InvestmentFond", on_delete=models.CASCADE)

    class Meta:
        db_table = "fond_comment"


class FondChatRoom(ChatRoom):
    """Model to store FondChatRooms"""

    fond = models.ForeignKey("fonds.InvestmentFond", on_delete=models.CASCADE)

    class Meta:
        db_table = "fond_chat_room"

    def __str__(self):
        return str(self.fond)
