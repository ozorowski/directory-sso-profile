'''
Django settings for sso-profile project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
'''

import os

from directory_components.constants import IP_RETRIEVER_NAME_GOV_UK
import directory_healthcheck.backends
import environ


env = environ.Env()
env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', False)

# As the app is running behind a host-based router supplied by Heroku or other
# PaaS, we can open ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'raven.contrib.django.raven_compat',
    'django.contrib.sessions',
    'django.contrib.contenttypes',  # required by DRF, not using any DB
    'django.contrib.auth',
    'captcha',
    'core',
    'directory_constants',
    'directory_components',
    'profile',
    'enrolment',
    'directory_healthcheck',
    'export_elements',
]

MIDDLEWARE_CLASSES = [
    'directory_components.middleware.MaintenanceModeMiddleware',
    'directory_components.middleware.IPRestrictorMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.PrefixUrlMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'sso.middleware.SSOUserMiddleware',
    'directory_components.middleware.NoCacheMiddlware',
    'directory_components.middleware.RobotsIndexControlHeaderMiddlware',
]

FEATURE_URL_PREFIX_ENABLED = env.bool('FEATURE_URL_PREFIX_ENABLED', False)
URL_PREFIX_DOMAIN = env.str('URL_PREFIX_DOMAIN', '')
if FEATURE_URL_PREFIX_ENABLED:
    ROOT_URLCONF = 'conf.urls_prefixed'
else:
    ROOT_URLCONF = 'conf.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'sso.context_processors.sso_processor',
                'directory_components.context_processors.urls_processor',
                ('directory_components.context_processors.'
                 'header_footer_processor'),
                'directory_components.context_processors.sso_processor',
                'directory_components.context_processors.analytics',
                'directory_components.context_processors.feature_flags',
                'directory_components.context_processors.cookie_notice',
            ],
        },
    },
]

WSGI_APPLICATION = 'conf.wsgi.application'


VCAP_SERVICES = env.json('VCAP_SERVICES', {})

if 'redis' in VCAP_SERVICES:
    REDIS_URL = VCAP_SERVICES['redis'][0]['credentials']['uri']
else:
    REDIS_URL = env.str('REDIS_URL', '')

if REDIS_URL:
    cache = {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': "django_redis.client.DefaultClient",
        }
    }
else:
    cache = {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }

CACHES = {
    'default': cache,
    'api_fallback': cache,
}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# Static files served with Whitenoise and AWS Cloudfront
# http://whitenoise.evans.io/en/stable/django.html#instructions-for-amazon-cloudfront
# http://whitenoise.evans.io/en/stable/django.html#restricting-cloudfront-to-static-files
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_HOST = env.str('STATIC_HOST', '')
STATIC_URL = STATIC_HOST + '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Logging for development
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': True,
            },
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        }
    }
else:
    # Sentry logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s '
                          '%(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR',
                'class': (
                    'raven.contrib.django.raven_compat.handlers.SentryHandler'
                ),
                'tags': {'custom-tag': 'x'},
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }

# SSO API Client
DIRECTORY_SSO_API_CLIENT_BASE_URL = env.str('SSO_API_CLIENT_BASE_URL', '')
DIRECTORY_SSO_API_CLIENT_API_KEY = env.str('SSO_SIGNATURE_SECRET', '')
DIRECTORY_SSO_API_CLIENT_SENDER_ID = env.str(
    'DIRECTORY_SSO_API_CLIENT_SENDER_ID', 'directory'
)
DIRECTORY_SSO_API_CLIENT_DEFAULT_TIMEOUT = 15

SSO_PROXY_LOGIN_URL = env.str('SSO_PROXY_LOGIN_URL')
SSO_PROXY_LOGOUT_URL = env.str('SSO_PROXY_LOGOUT_URL')
SSO_PROXY_SIGNUP_URL = env.str('SSO_PROXY_SIGNUP_URL')
SSO_PROXY_PASSWORD_RESET_URL = env.str('SSO_PROXY_PASSWORD_RESET_URL')
SSO_PROXY_REDIRECT_FIELD_NAME = env.str('SSO_PROXY_REDIRECT_FIELD_NAME')
SSO_SESSION_COOKIE = env.str('SSO_SESSION_COOKIE')
SSO_PROFILE_URL = env.str('SSO_PROFILE_URL')
SSO_PROXY_API_OAUTH2_BASE_URL = env.str('SSO_PROXY_API_OAUTH2_BASE_URL')

SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', True)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', 16070400)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# HEADER AND FOOTER LINKS
DIRECTORY_CONSTANTS_URL_EXPORT_READINESS = env.str(
    'DIRECTORY_CONSTANTS_URL_EXPORT_READINESS', ''
)
DIRECTORY_CONSTANTS_URL_EXPORT_OPPORTUNITIES = env.str(
    'DIRECTORY_CONSTANTS_URL_EXPORT_OPPORTUNITIES', ''
)
DIRECTORY_CONSTANTS_URL_SELLING_ONLINE_OVERSEAS = env.str(
    'DIRECTORY_CONSTANTS_URL_SELLING_ONLINE_OVERSEAS', ''
)
DIRECTORY_CONSTANTS_URL_EVENTS = env.str(
    'DIRECTORY_CONSTANTS_URL_EVENTS', ''
)
DIRECTORY_CONSTANTS_URL_INVEST = env.str('DIRECTORY_CONSTANTS_URL_INVEST', '')
DIRECTORY_CONSTANTS_URL_FIND_A_SUPPLIER = env.str(
    'DIRECTORY_CONSTANTS_URL_FIND_A_SUPPLIER', ''
)
DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON = env.str(
    'DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON', ''
)
DIRECTORY_CONSTANTS_URL_FIND_A_BUYER = env.str(
    'DIRECTORY_CONSTANTS_URL_FIND_A_BUYER', ''
)


PRIVACY_COOKIE_DOMAIN = env.str('PRIVACY_COOKIE_DOMAIN')

# Sentry
RAVEN_CONFIG = {
    'dsn': env.str('SENTRY_DSN', ''),
}

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', True)
SESSION_COOKIE_NAME = env.str('SESSION_COOKIE_NAME', 'profile_sessionid')
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True

# Google tag manager
GOOGLE_TAG_MANAGER_ID = env.str('GOOGLE_TAG_MANAGER_ID')
GOOGLE_TAG_MANAGER_ENV = env.str('GOOGLE_TAG_MANAGER_ENV', '')
UTM_COOKIE_DOMAIN = env.str('UTM_COOKIE_DOMAIN')


EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME = env.str(
    'EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME', ''
)
EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD = env.str(
    'EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD', ''
)
EXPORTING_OPPORTUNITIES_API_BASE_URL = env.str(
    'EXPORTING_OPPORTUNITIES_API_BASE_URL'
)
EXPORTING_OPPORTUNITIES_API_SECRET = env.str(
    'EXPORTING_OPPORTUNITIES_API_SECRET'
)
EXPORTING_OPPORTUNITIES_SEARCH_URL = env.str(
    'EXPORTING_OPPORTUNITIES_SEARCH_URL'
)

# find a buyer
FAB_REGISTER_URL = env.str('FAB_REGISTER_URL')
FAB_EDIT_COMPANY_LOGO_URL = env.str('FAB_EDIT_COMPANY_LOGO_URL')
FAB_EDIT_PROFILE_URL = env.str('FAB_EDIT_PROFILE_URL')
FAB_ADD_CASE_STUDY_URL = env.str('FAB_ADD_CASE_STUDY_URL')
FAB_ADD_USER_URL = env.str('FAB_ADD_USER_URL')
FAB_REMOVE_USER_URL = env.str('FAB_REMOVE_USER_URL')
FAB_TRANSFER_ACCOUNT_URL = env.str('FAB_TRANSFER_ACCOUNT_URL')

# feature flags
FEATURE_FLAGS = {
    'BUSINESS_PROFILE_ON': env.bool(
        'FEATURE_BUSINESS_PROFILE_ENABLED', False
    ),
    'EXPORT_JOURNEY_ON': env.bool('FEATURE_EXPORT_JOURNEY_ENABLED', True),
    # used by directory-components
    'MAINTENANCE_MODE_ON': env.bool('FEATURE_MAINTENANCE_MODE_ENABLED', False),
    # used by directory-components
    'SEARCH_ENGINE_INDEXING_OFF': env.bool(
        'FEATURE_SEARCH_ENGINE_INDEXING_DISABLED', False
    ),
    'NEW_ACCOUNT_JOURNEY_ON': env.bool(
        'FEATURE_NEW_ACCOUNT_JOURNEY_ENABLED', False
    ),
    'NEW_ACCOUNT_JOURNEY_SELECT_BUSINESS_ON': env.bool(
        'FEATURE_NEW_ACCOUNT_JOURNEY_SELECT_BUSINESS_ENABLED', True
    )

}

# Healthcheck
DIRECTORY_HEALTHCHECK_TOKEN = env.str('HEALTH_CHECK_TOKEN')
DIRECTORY_HEALTHCHECK_BACKENDS = [
    directory_healthcheck.backends.SingleSignOnBackend,
]


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

# ip-restrictor
IP_RESTRICTOR_SKIP_CHECK_ENABLED = env.bool(
    'IP_RESTRICTOR_SKIP_CHECK_ENABLED', False
)
IP_RESTRICTOR_SKIP_CHECK_SENDER_ID = env.str(
    'IP_RESTRICTOR_SKIP_CHECK_SENDER_ID', ''
)
IP_RESTRICTOR_SKIP_CHECK_SECRET = env.str(
    'IP_RESTRICTOR_SKIP_CHECK_SECRET', ''
)
IP_RESTRICTOR_REMOTE_IP_ADDRESS_RETRIEVER = env.str(
    'IP_RESTRICTOR_REMOTE_IP_ADDRESS_RETRIEVER',
    IP_RETRIEVER_NAME_GOV_UK
)
RESTRICT_ADMIN = env.bool('IP_RESTRICTOR_RESTRICT_IPS', False)
ALLOWED_ADMIN_IPS = env.list('IP_RESTRICTOR_ALLOWED_ADMIN_IPS', default=[])
ALLOWED_ADMIN_IP_RANGES = env.list(
    'IP_RESTRICTOR_ALLOWED_ADMIN_IP_RANGES', default=[]
)
RESTRICTED_APP_NAMES = env.list(
    'IP_RESTRICTOR_RESTRICTED_APP_NAMES', default=['admin']
)
if env.bool('IP_RESTRICTOR_RESTRICT_UI', False):
    # restrict all pages that are not in apps API, healthcheck, admin, etc
    RESTRICTED_APP_NAMES.append('')

# Google captcha
RECAPTCHA_PUBLIC_KEY = env.str('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = env.str('RECAPTCHA_PRIVATE_KEY')
# NOCAPTCHA = True turns on version 2 of recaptcha
NOCAPTCHA = env.bool('NOCAPTCHA', True)

# Companies House Search
DIRECTORY_CH_SEARCH_CLIENT_BASE_URL = env.str(
    'DIRECTORY_CH_SEARCH_CLIENT_BASE_URL'
)
DIRECTORY_CH_SEARCH_CLIENT_API_KEY = env.str(
    'DIRECTORY_CH_SEARCH_CLIENT_API_KEY'
)
DIRECTORY_CH_SEARCH_CLIENT_SENDER_ID = env.str(
    'DIRECTORY_CH_SEARCH_CLIENT_SENDER_ID', 'directory'
)
DIRECTORY_CH_SEARCH_CLIENT_DEFAULT_TIMEOUT = env.str(
    'DIRECTORY_CH_SEARCH_CLIENT_DEFAULT_TIMEOUT', 5
)

# getAddress.io
GET_ADDRESS_API_KEY = env.str('GET_ADDRESS_API_KEY')

# directory forms api client
DIRECTORY_FORMS_API_BASE_URL = env.str('DIRECTORY_FORMS_API_BASE_URL')
DIRECTORY_FORMS_API_API_KEY = env.str('DIRECTORY_FORMS_API_API_KEY')
DIRECTORY_FORMS_API_SENDER_ID = env.str('DIRECTORY_FORMS_API_SENDER_ID')
DIRECTORY_FORMS_API_DEFAULT_TIMEOUT = env.int(
    'DIRECTORY_API_FORMS_DEFAULT_TIMEOUT', 5
)

# gov.uk notify
CONFIRM_VERIFICATION_CODE_TEMPLATE_ID = env.str(
    'CONFIRM_VERIFICATION_CODE_TEMPLATE_ID',
    'aa4bb8dc-0e54-43d1-bcc7-a8b29d2ecba6'
)

GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID',
    '5c8cc5aa-a4f5-48ae-89e6-df5572c317ec'
)
GOV_NOTIFY_REQUEST_COLLABORATION_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_REQUEST_COLLABORATION_TEMPLATE_ID',
    '02b0223f-2674-4b0b-bdcc-df21dabbc743'
)

# directory api
DIRECTORY_API_CLIENT_BASE_URL = env.str('DIRECTORY_API_CLIENT_BASE_URL')
DIRECTORY_API_CLIENT_API_KEY = env.str('DIRECTORY_API_CLIENT_API_KEY')
DIRECTORY_API_CLIENT_SENDER_ID = env.str(
    'DIRECTORY_API_CLIENT_SENDER_ID', 'directory'
)
DIRECTORY_API_CLIENT_DEFAULT_TIMEOUT = env.str(
    'DIRECTORY_API_CLIENT_DEFAULT_TIMEOUT', 15
)

# directory client core
DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS = 60 * 60 * 24 * 30  # 30 days
