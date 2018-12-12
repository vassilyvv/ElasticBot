"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 2.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

from django.core.exceptions import ImproperlyConfigured


def get_env_setting(setting, default=None):
    """ Get the environment setting or return exception """
    try:
        return os.environ[setting]
    except KeyError:
        if default is not None:
            return default
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = bool(int(get_env_setting('DEBUG')))
USE_S3 = bool(int(get_env_setting('USE_S3', '0')))
IS_DOCKER = bool(int(get_env_setting('DOCKER', '0')))
SECRET_KEY = get_env_setting('SECRET_KEY')
ALLOWED_HOSTS = get_env_setting('ALLOWED_HOSTS').split(',')
TELEGRAM_TOKEN = get_env_setting('TELEGRAM_TOKEN', '')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'mptt',

    'project.tgbot',
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

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
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

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_env_setting('POSTGRES_DB'),
        'USER': get_env_setting('POSTGRES_USER'),
        'PASSWORD': get_env_setting('POSTGRES_PASSWORD'),
        'HOST': get_env_setting('POSTGRES_HOST'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'project/static')
]
if not DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

if IS_DOCKER:
    MEDIA_ROOT = '/data/django/media/'
    STATIC_ROOT = '/data/django/static/'

else:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

REST_FRAMEWORK = {
    'DATETIME_FORMAT': '%s',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if USE_S3:
    STATICFILES_LOCATION = 'static'
    MEDIAFILES_LOCATION = 'media'
    STATICFILES_STORAGE = 'project.storages.StaticStorage'
    DEFAULT_FILE_STORAGE = 'project.storages.MediaStorage'

    AWS_STORAGE_BUCKET_NAME = get_env_setting('S3_STORAGE_BUCKET')
    AWS_S3_REGION_NAME = get_env_setting('AWS_DEFAULT_REGION')  # e.g. us-east-2
    AWS_ACCESS_KEY_ID = get_env_setting('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = get_env_setting('AWS_SECRET_ACCESS_KEY')
    AWS_S3_SECURE_URLS = True

    STATIC_CACHE_CONTROL = 'max-age=2592000'  # 30 days
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': STATIC_CACHE_CONTROL,
    }
    AWS_IS_GZIPPED = True

    # Tell django-storages the domain to use to refer to static files.
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
else:
    MEDIA_URL = '/media/'
    STATIC_URL = '/static/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = get_env_setting('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_setting('EMAIL_HOST_PASSWORD')

ASGI_APPLICATION = 'project.routing.application'
REDIS_HOST = 'redis'
if not IS_DOCKER:
    REDIS_HOST = 'localhost'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(REDIS_HOST, 6379)],
        },
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',  # change debug level as appropiate
            'propagate': False,
        },
    },
}