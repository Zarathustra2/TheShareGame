"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from django.urls import path

from stats import views

app_name = "stats"

urlpatterns = [path("<slug:isin>/key_figures/", views.PastKeyFiguresListApiView.as_view(), name="past_key_figures")]
