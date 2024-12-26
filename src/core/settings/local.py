# ruff: noqa
import logging

from .base import *

APP_ENV = env("APP_ENV", default="local")

# ALLOWED_HOSTS=reporthub.immap.org,www.reporthub.immap.org
# env.list() splits comma-separated string into a list
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

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
        "NAME": env("DB_NAME", default="test"),
        "USER": env("DB_USER", default="root"),
        "PASSWORD": env("DB_PASSWORD", default=""),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="3306"),
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

####################
# DB Backup Settings
####################
DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_SEND_EMAIL = False
DBBACKUP_STORAGE_OPTIONS = {"location": os.path.join(BASE_DIR.parent, "db-backups")}


# Can use MailTrap SMTP Setup for now (dev and staging only).
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = env("EMAIL_HOST", default="smtp.mailtrap.io")
EMAIL_PORT = env("EMAIL_PORT", default=587)  # 2525
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="reporthub@immap.org")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="reporthub@immap.org")
EMAIL_USE_SSL = env("EMAIL_USE_SSL", default=False)
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=True)

# CACHE
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}
