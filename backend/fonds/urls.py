"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from django.urls import path

from . import views

app_name = "fonds"

urlpatterns = [
    path("", views.InvestmentFondAPICreateListView.as_view(), name="fonds"),
    path("<int:fond_id>/", views.InvestmentFondRetrieveAPIView.as_view(), name="fond"),
    path("<int:fond_id>/slim/", views.InvestmentFondSlimRetrieveAPIView.as_view(), name="fond_slim"),
    path("<int:fond_id>/profile/", views.FondProfileUpdateRetrieveView.as_view(), name="fond_profile"),
    path("<int:fond_id>/threads/", views.FondThreadListCreateAPIView.as_view(), name="forum"),
    path("<int:fond_id>/threads/<int:thread_id>/", views.FondThreadPostListCreateAPIView.as_view(), name="thread"),
    path("<int:fond_id>/applications/", views.FondApplicationCreateListView.as_view(), name="applications"),
    path(
        "<int:fond_id>/applications/<int:application_id>/",
        views.FondApplicationDestroyView.as_view(),
        name="application_destroy",
    ),
    path("user_data/", views.UserFondRetrieveView.as_view(), name="user_fond_data"),
]
