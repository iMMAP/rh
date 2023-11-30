# ruff: noqa
from .base import *

DATABASES = {
    "sqlite": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR.parent / "db.sqlite3",
    },
    # "mysql": {
    #     "ENGINE": "django.db.backends.mysql",
    #     "NAME": env("DB_NAME", default="rh"),
    #     "USER": env("DB_USER", default="root"),
    #     "PASSWORD": env("DB_PASSWORD", default=""),
    #     "HOST": env("DB_HOST", default="localhost"),
    #     "PORT": env("DB_PORT", default="3306"),
    #     "OPTIONS": {"charset": "utf8mb4"},
    # },
}

DB = env("DB", default="sqlite")

DATABASES["default"] = DATABASES[DB]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage", # with cashing
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",  # No Caching
    },
}


DJANGO_VITE_PLUGIN = {
    "BUILD_DIR": "static-cdn/build",
    "BUILD_URL_PREFIX": "/" + STATIC_URL + "build",
    "DEV_MODE": False,
    "STATIC_LOOKUP": False,
}
