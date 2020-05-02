"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from django.urls import path
from rest_framework import routers

from users import views

app_name = "users"

router = routers.SimpleRouter()
router.register(r"users", views.UsersViewSet, "users")

urlpatterns = [
    path("register/", views.RegistrationAPI.as_view(), name="register_user"),
    path("login/", views.LoginAPI.as_view(), name="login"),
    path("articles/", views.ArticleListCreateAPIView.as_view(), name="articles"),
    path("articles/<int:article_id>/comments/", views.CommentListCreateAPIView.as_view(), name="article_comments"),
    path("companies/<slug:isin>/articles/", views.ArticleCompanyListAPIView.as_view(), name="articles_company"),
    path("threads/", views.ThreadListCreateAPIView.as_view(), name="threads"),
    path("threads/<int:thread_id>/posts/", views.ThreadPostListCreateAPIView.as_view(), name="thread_posts"),
    path(
        "threads/<int:thread_id>/posts/<int:post_id>/",
        views.ThreadPostDestroyUpdateView.as_view(),
        name="thread_post_destroy_update",
    ),
    path("conversations/", views.ConversationListCreateAPIView.as_view(), name="conversations"),
    path("conversations/<int:conversation_id>/", views.MessagesListCreateAPIView.as_view(), name="messages"),
    path("notifications/", views.NotificationListAPIView.as_view(), name="notifications"),
    path("notifications/<int:id>/", views.NotificationRetrieveView.as_view(), name="notification"),
    path("unread/", views.UnreadRetrieveView.as_view(), name="unread"),
    path("active/", views.ActiveUserRetrieveView.as_view(), name="active_user"),
    path("profile/<int:id>/", views.ProfileRetrieveUpdateView.as_view(), name="profile"),
]

urlpatterns += router.urls
