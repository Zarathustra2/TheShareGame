"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""
import inspect
import logging
import logging.config
import os
import os
import sys
from distutils.util import strtobool

from django.utils.log import DEFAULT_LOGGING

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "LOCALHOST_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
#
# docker-compose does not pass booleans. It passes the values as string.
# So we convert the value from string to bool.
DEBUG = strtobool(os.environ.get("DEBUG", "True"))

ALLOWED_HOSTS = ["backend", "localhost", "127.0.0.1", "167.172.96.133", "www.thesharegame.com", "thesharegame.com"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # third party
    "rest_framework",
    "rest_framework.authtoken",

    "django_countries",
    "corsheaders",

    "celery",

    "rest_auth",

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',

    # my apps
    "stats",
    "core.apps.CoreConfig",
    "users.apps.UsersConfig",
    "fonds.apps.FondsConfig",
    "common.apps.CommonConfig",
    "periodic_tasks",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "tsg.middleware.RequestTimeMiddleware",
]

if DEBUG:
    MIDDLEWARE = MIDDLEWARE + ["tsg.middleware.QueryCountDebugMiddleware"]

CORS_ORIGIN_WHITELIST = (
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost:80",
    "http://localhost",
    "https://thesharegame.com",
    "https://www.thesharegame.com",
)

ROOT_URLCONF = "tsg.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "tsg.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "tsg_db"),
        "USER": os.environ.get("POSTGRES_USER", "tsg_user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "tsg_password"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", ""),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = "/static/"

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    'COERCE_DECIMAL_TO_STRING': False,

    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
}


# Disable the browsable api in production and use only json
# if DEBUG is False:
#     REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
#         'rest_framework.renderers.JSONRenderer',
#     ]

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

LOGGING_CONFIG = None

LOGLEVEL = os.environ.get('LOGLEVEL', 'info').upper()

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        # console logs to stderr
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
    },
    'loggers': {
        # default for all undefined Python modules
        '': {
            'level': LOGLEVEL,
            'handlers': ['console', ],
        },

        'celery': {
            'level': LOGLEVEL,
            'handlers': ['console', ],
            'propagate': False,
        },

        # Default runserver request logging
        'django.server': DEFAULT_LOGGING['loggers']['django.server'],
    },
})

# if run on circle ci, do not show any logs
if os.environ.get("CI", None):
    logging.disable(logging.CRITICAL)

# Disable debugging in celery. Celery prints every SQL Query.
# For debugging SQL queries this is useful but outside of that it can get kinda annoying.
# So we disable it for development.
if "celery" in sys.argv[0]:
    DEBUG = False

CELERY_IMPORTS = (
    'periodic_tasks.jobs',
)

if DEBUG is False:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    DJANGO_SENTRY_DSN = os.environ.get("DJANGO_SENTRY_DSN", "")
    if DJANGO_SENTRY_DSN == "":
        logging.error("DJANGO_SENTRY_DSN is not set!")
    else:
        sentry_sdk.init(
            # TODO: Probably env file
            dsn=DJANGO_SENTRY_DSN,
            integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()]
        )

STATIC_URL = "/staticfiles/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/mediafiles/"
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")

logging.info(f"Running in {'Development' if DEBUG else 'Production'}")

# Disable email verification for now
ACCOUNT_EMAIL_VERIFICATION = "none"

RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY", "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe")

if RECAPTCHA_SECRET_KEY == "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe":
    logging.warning("Using test recaptcha key. All requests will succeed! Don't use in production!")

    if DEBUG is False:

        # Log an error if it is the api backend. For celery we don't need the key.
        if not ("celery" in sys.argv[0]):
            logging.error("Test recaptcha used in production! Resetting key.")
        RECAPTCHA_SECRET_KEY = ""

if not DEBUG:
    # SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_REFERRER_POLICY = 'same-origin'
