import os
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR.parent, ".env"))

SECRET_KEY = env("SECRET_KEY", default="unsafe-secret-key")

DJANGO_SETTINGS_MODULE = env("DJANGO_SETTINGS_MODULE", default="core.settings.local")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", default=True)

ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    # Default django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Installed packages apps
    "django_filters",
    "smart_selects",
    "django_vite_plugin",
    "import_export",
    "django_htmx",
    "compressor",
    # RH apps
    "rh.apps.RhConfig",
    "users.apps.UsersConfig",
    "stock.apps.StockConfig",
    "project_reports.apps.ProjectReportsConfig",
]
USE_DJANGO_JQUERY = True

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "core.middleware.MaintenanceModeMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "rh.context_processors.env_variables",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

DATA_UPLOAD_MAX_NUMBER_FIELDS = 50240

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "users.backends.EmailBackend",
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]


STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "static-cdn"

# Base URL to serve media files
MEDIA_URL = '/media/'

# Directory where media files are stored
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

COMPRESS_ENABLED = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/profile/"
LOGOUT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Can use MailTrap SMTP Setup for now (dev and staging only).
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"


EMAIL_HOST = env("EMAIL_HOST", default="smtp.mailtrap.io")
EMAIL_PORT = env("EMAIL_PORT", default=587)  # 2525
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="reporthub@immap.org")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="reporthub@immap.org")
EMAIL_USE_SSL = env("EMAIL_USE_SSL", default=False)
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=True)


####################
# Maintence mode Settings
####################
MAINTENANCE_MODE_ENABLED = env("MAINTENANCE_MODE_ENABLED", default=False)
# if True the superuser will not see the maintenance-mode page
MAINTENANCE_MODE_IGNORE_SUPERUSER = env("MAINTENANCE_MODE_IGNORE_SUPERUSER", default=True)
# if True the staff will not see the maintenance-mode page
MAINTENANCE_MODE_IGNORE_STAFF = env("MAINTENANCE_MODE_IGNORE_STAFF", default=True)
# the absolute url where users will be redirected to during maintenance-mode
MAINTENANCE_MODE_REDIRECT_ROUTE = env("MAINTENANCE_MODE_REDIRECT_ROUTE", default="maintenance")
# secret code to bypass maintenance mode for the user
# /reporthub.immap.org/?MAINTENANCE_BYPASS_QUERY
MAINTENANCE_BYPASS_QUERY = env("MAINTENANCE_BYPASS_QUERY", default="")
