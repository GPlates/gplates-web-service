"""
Django settings for GWS project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import queue
import random
import string
import sys

from dotenv import load_dotenv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)  # call dirname() twice to get "../"

sys.path.append(f"{BASE_DIR}/lib")

load_dotenv(f"{BASE_DIR}/.env")  # take environment variables from .env.

EARTH_STORE_DIR = f"{BASE_DIR}/data/earth/"
PALEO_STORE_DIR = f"{BASE_DIR}/data/paleo/"
MODEL_REPO_DIR = f"{BASE_DIR}/data/model-repo/"
MOBILE_APP_DIR = f"{BASE_DIR}/data/mobile-app"

MODEL_DEFAULT = "MULLER2019"

MEDIA_ROOT = f"{BASE_DIR}/data/tmp/"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key safe!
# ************
# SEE HERE!!! best to put the SECRET_KEY in your .env file
# ************
SECRET_KEY = os.getenv("SECRET_KEY")
# alternatively, put SECRET_KEY here, but do not submit the SECRET_KEY to code repository
# SECRET_KEY = 'put your secret key here' # better not do this!!!
if not SECRET_KEY:
    SECRET_KEY = "".join(
        random.choice(string.ascii_letters + string.digits + string.punctuation)
        for i in range(24)
    )
    print(
        "SECRET_KEY not found!!! Check your .env and settings.py!! Use random string for now!"
    )


# SECURITY WARNING: don't run with debug turned on in production!
if os.getenv("DEBUG") and os.getenv("DEBUG").lower() == "true":
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ["*"]

# if empty, there is no access control.
ACCESS_CONTROL_URL = "https://portal.gplates.org/access_control/"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admindocs",
    "rest_framework",
    # 'rest_framework_swagger',
    "reconstruct",
    "rotation",
    "topology",
    "earth",
    "doc",
    "plate_model",
    "paleomap",
    "mobile",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "GWS.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "GWS.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    "default": {
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.getenv(
            "DB_NAME"
        ),  # Database name. Or path to database file if using sqlite3.
        # Database username. Not used with sqlite3.
        "USER": os.getenv("DB_USER"),
        "HOST": os.getenv("DB_HOST"),  # Database hostname
        "PASSWORD": os.getenv("DB_PASSWORD"),  # Database password for USER
        # Set to empty string for default. Not used with sqlite3.
        "PORT": os.getenv("DB_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = "/var/www/html/static/"
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

DEFAULT_THROTTLE_ANON_RATE = os.getenv("DEFAULT_THROTTLE_ANON_RATE") or "10000/second"

DEFAULT_THROTTLE_USER_RATE = os.getenv("DEFAULT_THROTTLE_USER_RATE") or "10000/second"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": DEFAULT_THROTTLE_ANON_RATE,
        "user": DEFAULT_THROTTLE_USER_RATE,
    },
}

# flag to indicate if the traffic should be throttled.
THROTTLE = os.getenv("THROTTLE") and os.getenv("THROTTLE").lower() == "true"

if DEBUG:
    logger_level = "DEBUG"
    THROTTLE = False
    disable_existing_loggers_flag = False
else:
    logger_level = "ERROR"
    disable_existing_loggers_flag = True


LOGGING = {
    "version": 1,
    "disable_existing_loggers": disable_existing_loggers_flag,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "logfile": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"/gws/log/error.log",
            "maxBytes": 50000,
            "backupCount": 2,
            "formatter": "standard",
        },
        "access_log": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"/gws/log/access.log",
            "maxBytes": 5000000,
            "backupCount": 99,
            "formatter": "standard",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "mail_admins": {
            "level": "CRITICAL",
            "class": "django.utils.log.AdminEmailHandler",
        },
        "queue": {
            "level": "INFO",
            "class": "utils.queue_listener_handler.QueueListenerHandler",
            "handlers": ["cfg://handlers.access_log"],
            "queue": "cfg://objects.queue",
        },
    },
    "loggers": {
        "default": {
            "handlers": ["console", "logfile", "mail_admins"],
            "level": logger_level,
        },
        "queue": {
            "handlers": ["queue"],
            "level": "INFO",
        },
    },
    "objects": {"queue": {"class": "queue.Queue", "maxsize": 1000}},
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    },
    "redis": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://gws-redis:6379",
    },
}


def get_cache_name():
    name = os.getenv("CACHE")
    return name if name else "default"
