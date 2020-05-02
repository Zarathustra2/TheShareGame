"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""
from django.conf.urls.static import static

from tsg import settings

"""tsg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.documentation import include_docs_urls
from .views import GithubLogin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path("api/stats/", include("stats.urls")),
    path("api/social/", include("users.urls")),
    path("api/fonds/", include("fonds.urls")),
    path("api-token-auth/", obtain_auth_token),
    path("docs/", include_docs_urls(title="TheShareGame API", public=True)),
    path("api/auth/github/", GithubLogin.as_view(), name="github_login"),
    path("accounts/", include("allauth.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
