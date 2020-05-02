"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""
from __future__ import annotations

import logging
import os
from io import BytesIO

from decimal import Decimal

from django.contrib.auth.models import AbstractUser, UserManager
from django.core.files.base import ContentFile
from django.db import models, IntegrityError
from django.template.defaultfilters import slugify
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
from unidecode import unidecode

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from PIL import ImageDraw, ImageFont, Image

from common.storage import OverwriteStorage

logger = logging.getLogger(__name__)


class UserManagerCustom(UserManager):
    @classmethod
    def _check_username_unique(cls, username) -> None:
        """Check no other user exists with the given username - case-insensitive."""
        if User.objects.filter(username__iexact=username).exists() or username is None:
            raise IntegrityError("Username is not unique!")

    def create_user(self, username, email=None, password=None, **extra_fields):
        self._check_username_unique(username)
        return super().create_user(username, email, password, **extra_fields)

    def create(self, **kwargs):
        self._check_username_unique(kwargs.get("username"))
        return super().create(**kwargs)


class User(AbstractUser):
    """
	Users within the django authentication are represented with this model

	Instead of using the django-base-user we create our own model, so we can adjust it easily.
	"""

    objects = UserManagerCustom()
    email = models.EmailField(_("email address"), blank=True, unique=True)

    class Meta:
        db_table = "user"

    def get_token(self) -> str:
        """Returns the authentication Token for the API"""
        return str(Token.objects.get(user=self))

    @cached_property
    def is_ingame_admin(self) -> bool:
        """Returns whether the user is an admin ingame"""
        logger.error("Implement Admin Model and then adjust Thread Test Case")
        return False

    @cached_property
    def has_fond(self) -> bool:
        """Returns whether the user is in a fond"""
        from fonds.models import Member

        return Member.objects.filter(user=self).exists()

    @cached_property
    def companies_book_value(self) -> Decimal:
        """Returns the total book value of all companies of the user"""
        return self.company.keyfigures.book_value


class Article(models.Model):
    """
	Model for storing Newspaper-Articles

	Companies as well as Fonds can write articles, which can be read
	by all users in the newspaper.

    They submit articles, which then get accepted/declined by the admins.

	:headline: The headline of the article
	:text: The actual article
	:slug: The slug of the article. Created through the headline
	:accepted: Boolean whether the article got accepted or not by the administration
	:date_time: The time the article was submitted
	"""

    headline = models.CharField(max_length=25, null=False)
    text = models.TextField()

    slug = models.SlugField()

    accepted = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        db_table = "article"

    def __str__(self):
        return self.headline

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.headline))

        class_ = self.__class__.__name__
        if class_ not in ("CompanyArticle", "FondArticle") and self.pk is None:
            logger.error(f"{class_} is neither a subclass of CompanyArticle nor of FondArticle")
            raise Exception("Articles can only be created with subclasses")

        super().save(*args, **kwargs)


class CompanyArticle(Article):
    """Model for Articles written by a Company"""

    company = models.ForeignKey("core.Company", on_delete=models.CASCADE)

    class Meta:
        db_table = "company_article"


class Comment(models.Model):
    """
	Model to store Comments related to an article,
    User and Fonds can comment on articles to ask questions or
    critizes something.

	:article: The article the comment belongs to
	:text: The actual comment
	:date_time: The time the comment was created
	"""

    id = models.BigAutoField(primary_key=True, editable=False)

    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    text = models.TextField()

    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        db_table = "comment"


class UserComment(Comment):
    """Model to store User-Comments"""

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "user_comment"


class BaseThread(models.Model):
    """
	Model for storing Threads of the Public-Forum.

    A thread is always about a certain topic. Each thread has multiple
    posts.

    A thread can be locked, for instance, an official news thread should be
    locked so only admins can post something.

	:name: The name of the Thread
	:user: The user who created the thread
	:read_by: Users who have read this thread
	:slug: The slug of the thread. Created through the name
	:date_time: The time the thread was created
	:updated: The last time someone posted something in this thread
	:locked: Boolean. If locked than only admins can post in this thread
	:pinned: Boolean. If true, they will appear first in the order
	"""

    name = models.CharField(max_length=25, null=False)

    user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    read_by = models.ManyToManyField("users.User", related_name="read_threads")

    slug = models.SlugField(null=False, blank=False)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    locked = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BaseThreadPost(models.Model):
    """
	Model for storing Posts of a Thread

	:thread: The thread, which belong to the post
	:user: The user who created the thread
	:text: The actual post
	:date_time: The time this post was created
	"""

    user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)

    text = models.TextField()

    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True


class Thread(BaseThread):
    """
	Model for storing Threads of the Public-Forum

	:name: The name of the Thread
	:user: The user who created the thread
	:read_by: Users who have read this thread
	:slug: The slug of the thread. Created through the name
	:date_time: The time the thread was created
	:updated: The last time someone posted something in this thread
	:locked: Boolean. If locked than only admins can post in this thread
	:pinned: Boolean. If true, they will appear first in the order
	"""

    class Meta:
        db_table = "thread"


class ThreadPost(BaseThreadPost):
    """
	Model for storing Posts of a Thread

	:thread: The thread, which belong to the post
	:user: The user who created the thread
	:text: The actual post
	:date_time: The time this post was created
	"""

    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=False)

    class Meta:
        db_table = "thread_post"


class UnreadThread(models.Model):
    """Model to store the unread threads of a user"""

    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "unread_thread"


class ChatRoom(models.Model):
    """Model for ChatRooms"""

    name = models.CharField(max_length=25, null=False, blank=False)

    class Meta:
        db_table = "chat_room"

    def __str__(self):
        return self.name


class ChatMessage(models.Model):
    """Model for a Chat-Message"""

    text = models.CharField(max_length=100)

    id = models.BigAutoField(primary_key=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        db_table = "chat_message"

    def __str__(self):
        return f"{self.user}: {self.text}"


class Notification(models.Model):
    """
	Model for storing Notifications of a user.

	Notifications can be a BondPayBack, successful Buy-/Sell-Order
	and much more.

	:user: The user who receivers the notification
	:text: The actual notification
	:subject: The subject of the notification
	:date_time: The time the notification was sent
	"""

    id = models.BigAutoField(primary_key=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    text = models.TextField()

    # Ensure the subject is not null by setting the default none
    subject = models.CharField(max_length=255, blank=False, default=None)

    created = models.DateTimeField(auto_now_add=True, editable=False)

    read = models.BooleanField(default=False)

    class Meta:
        db_table = "notification"

    def __str__(self):
        return self.subject

    @classmethod
    def order(cls, user_id: int, amount: int, price: Decimal, order_of, received: bool) -> Notification:
        """
        Creates a new order notification.

        The notification created by this function has not been persisted to the database yet.
        """
        typ_order = f"{'Sell' if received else 'Buy'}-Order"
        text = f"Your {typ_order} for {order_of} has been matched!"
        text += f"\n\nAmount: {amount}\nPrice per share: {price}\nValue: {amount * price}$"

        subject = f"{typ_order} {order_of}"
        notification = Notification(user_id=user_id, subject=subject, text=text)
        return notification


class Conversation(models.Model):
    """
	Model to store conversations between multiple users.

    Conversations are private and only the participating users can read &
    send messages.

	:users: Participants of the conversations
	:read_by: Users who have read the latest message
	:subject: Subject of the conversation
	:date_time: start time of the conversation
	"""

    id = models.BigAutoField(primary_key=True, editable=False)

    users = models.ManyToManyField(User, related_name="conversations")
    unread_by = models.ManyToManyField(User, related_name="conversations_unread")

    subject = models.CharField(max_length=25)

    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        db_table = "conversation"

    def __str__(self):
        return self.subject

    @classmethod
    def create_new_conversation(cls, receivers_id: [int], subject: str, sender_id: int) -> Conversation:
        """
		Creates a new conversation and returns it

		:param receivers_id: The ids of users who should be in this conversation
		:param subject: The subject of the conversation
		:param sender_id: The user who started the conversation
		:return:
		"""

        obj = cls.objects.create(subject=subject)

        # with M2M fields it is best ot use the primary keys
        # this will result in less queries
        obj.users.add(sender_id, *receivers_id)
        obj.unread_by.add(*receivers_id)
        logger.info(f"New Conversation created: {subject} by {sender_id}")
        return obj

    @classmethod
    def welcome_msg(cls, user: User) -> None:
        """
        Welcomes a user by sending him/her a welcome message
        """

        superuser = User.objects.filter(is_superuser=True).first()

        if superuser is None:
            logger.warning("No superuser exists!")
            return

        msg = (
            f"Welcome {user.username},\n\n"
            "Glad you started TheShareGame. I hope you are having a good time.!\n"
            "My name is Dario and I created TheShareGame or in short TSG. If you have any questions, "
            "feel free to send me a message.\n\n"
            "Use the **Chat** to get in touch with others.\n\n"
            "As first steps I would suggest doing the following:\n\n"
            "- Buy 1 Bond for 100,000$\n"
            "- Buy some shares from a company. You can find all companies under Market -> Companies\n"
            "- Submit an article in our ingame newspaper and introduce your company.\n\n"
            "Best Regards,\n"
            f"{superuser.username}\n\n"
            "PS: If you are a programmer one can find the source code of the backend & frontend on "
            "[github.com/Zarathustra2/TheShareGame](https://www.github.com/Zarathustra2/TheShareGame)"
        )

        conv = cls.create_new_conversation([user.id], "Welcome", superuser.id)
        Message.create_new_message(conv.id, msg, superuser.id)


class Message(models.Model):
    """
	Model to store the messages of a conversation.

	:conversation: The conversation the message belongs to
	:sender: The user who sent the message
	:text: The actual message
	:date_time: The time the message was sent
	"""

    id = models.BigAutoField(primary_key=True, editable=False)

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)

    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sent_messages")

    text = models.TextField()

    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        db_table = "message"

    @classmethod
    def create_new_message(cls, conversation_id: int, text: str, sender_id: int) -> Message:
        """
		Creates a new message and updates the unread_by field
		in the conversation

		:param conversation_id: The id of the conversation this message belongs to
		:param text: The actual message
		:param sender_id: The user who sent the message
		:return:
		"""

        obj = cls.objects.create(conversation_id=conversation_id, text=text, sender_id=sender_id)

        obj.update_read_by()
        return obj

    def update_read_by(self) -> None:
        """
		Updates the read_by-field in the Conversation model
		by deleting everyone except the sender.
		"""

        obj = self.conversation
        sender_id = self.sender_id
        # ToDo: As long as we have this list comprehension
        # we limit the participants to 10....
        # ToDo. Find a better way...
        obj.unread_by.add(*[u for u in obj.users.exclude(id=sender_id).values_list("id", flat=True)])
        obj.unread_by.remove(sender_id)


def upload_location(instance, filename):
    _, extension = filename.split(".")
    name = instance.user.company.name
    name = name.replace(" ", "_")
    return "company_logo/%s.%s" % (name, extension)


class Profile(models.Model):
    """
    Model to store the profile of a user
    """

    IMAGE_W = 450
    IMAGE_H = 120

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(default="This user prefers to keep an air of mystery about them.")
    age = models.PositiveSmallIntegerField()

    company_logo = models.ImageField(upload_to=upload_location, default="logo_default.jpg", storage=OverwriteStorage())

    def __str__(self):
        return f"Profile {self.user.username}: Age: {self.age}"

    def create_default_logo(self) -> None:
        """
        Creates a default logo for the company of the given user.

        The default logo has the name of the company in the middle of the logo.
        """

        company = self.user.company
        if not company:
            logger.error(f"{self.user} does not have a company. Cannot create logo!")
            return

        img = Image.open(self.company_logo)

        draw = ImageDraw.Draw(img)
        try:
            arial = ImageFont.truetype("arial.ttf", 60)
        except OSError:
            logger.error("Could not load font arial.ttf!")
            return

        txt = company.name
        w, h = draw.textsize(txt, font=arial)
        draw.text(((self.IMAGE_W - w) / 2, (self.IMAGE_H - h) / 2), txt, (255, 255, 255), font=arial)

        f = BytesIO()
        try:
            img.save(f, format="png")
            s = f.getvalue()
            self.company_logo.save(f"{txt.strip('.')}.jpg", ContentFile(s))
        finally:
            f.close()
