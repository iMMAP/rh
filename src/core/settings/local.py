# ruff: noqa
import logging

from .base import *

APP_ENV = env("APP_ENV", default="local")

if not TESTING:
    INSTALLED_APPS = [
        *INSTALLED_APPS,
        "debug_toolbar",
    ]
    MIDDLEWARE = [
        *MIDDLEWARE,
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

LOCAL_INSTALLED_APPS = [
    "django_extensions",
    "nplusone.ext.django",
    "django_tui",
]

# Concatinate the local apps to the installed apps list of our base settings
INSTALLED_APPS = INSTALLED_APPS + LOCAL_INSTALLED_APPS


LOCAL_MIDDLEWARE = [
    "nplusone.ext.django.NPlusOneMiddleware",
]

MIDDLEWARE = MIDDLEWARE + LOCAL_MIDDLEWARE


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []


DATABASES = {
    "sqlite": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR.parent / "db.sqlite3",
    },
    "postgresql": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", default="rh"),
        "USER": env("DB_USER", default="postgres"),
        "PASSWORD": env("DB_PASSWORD", default="admin"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
    },
}

DB = env("DB", default="sqlite")

DATABASES["default"] = DATABASES[DB]

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]


STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
}

#
NPLUSONE_LOGGER = logging.getLogger("nplusone")
NPLUSONE_LOG_LEVEL = logging.WARN


DJANGO_VITE_PLUGIN = {
    "BUILD_DIR": "static-cdn/build",
    "BUILD_URL_PREFIX": "/" + STATIC_URL + "build",
    "DEV_MODE": True,
    "STATIC_LOOKUP": False,
    # "SERVER": {"HOST": "localhost", "PORT": 3000},
}
