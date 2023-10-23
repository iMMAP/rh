from .base import *

LOCAL_INSTALLED_APPS = [
    "debug_toolbar",
    "django_extensions",
    "nplusone.ext.django",
]

# Concatinate the local apps to the installed apps list of our base settings
INSTALLED_APPS = INSTALLED_APPS + LOCAL_INSTALLED_APPS


LOCAL_MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "nplusone.ext.django.NPlusOneMiddleware",
]

MIDDLEWARE = MIDDLEWARE + LOCAL_MIDDLEWARE


DATABASES = {
    "sqlite": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "postgresql": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", default="test"),
        "USER": env("DB_USER", default="root"),
        "PASSWORD": env("DB_PASSWORD", default=""),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="3306"),
    },
    "mysql": {
        "ENGINE": "django.db.backends.mysql",
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
    "staticfiles": {
        # "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage", # with cashing
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",  # No Caching
    },
}

#
NPLUSONE_LOGGER = logging.getLogger("nplusone")
NPLUSONE_LOG_LEVEL = logging.WARN