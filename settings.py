import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

env = environ.Env()
environ.Env.read_env()

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-4-vwuk3dtdi9jmc(&m4kqys%ltg_#rn0vt%z(=v2*9y68*@$9s'

SECRET_KEY = env("SECRET_KEY", default="unsafe-secret-key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG=True #env("DEBUG", default=True)

# For Testing the registration email confirmation, make debug=True
# DEBUG = False

ALLOWED_HOSTS = ['dev.reporthub.immap.org', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'rh.apps.RhConfig',
    'users.apps.UsersConfig',
    'stock.apps.StockConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [],
        'APP_DIRS': True,
        'DIRS': [BASE_DIR / 'templates'],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'

DATA_UPLOAD_MAX_NUMBER_FIELDS = 50240

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': env("DB_NAME"),
#         'USER': env("DB_USER"),
#         'PASSWORD': env("DB_PASSWORD"),
#         'HOST': env("DB_HOST"),
#         'PORT': env("DB_PORT"),
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static-cdn'
STATICFILES_DIRS = [
   BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/profile/'
LOGOUT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Can use MailTrap SMTP Setup for now (dev and staging only).
EMAIL_HOST = env('EMAIL_HOST')  # 'smtp.mailtrap.io'
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_PORT = env('EMAIL_PORT')  # 2525

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = env('EMAIL_HOST')  # 'smtp.mailtrap.io'
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = env('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
# EMAIL_PORT = env('EMAIL_PORT')  # 587
