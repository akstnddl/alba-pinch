"""운영 환경 설정 (NHN Cloud)"""
import dj_database_url
from decouple import Csv

from .base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())  # noqa

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),  # noqa
        conn_max_age=600,
    )
}

# HTTPS 강제
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 60 * 60 * 24 * 180
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=Csv())  # noqa

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
