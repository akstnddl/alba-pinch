"""개발 환경 설정"""
from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# 개발용은 SQLite로 간단하게
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # noqa
    }
}
# 로컬 테스트도 진짜 메일 발송 (base.py의 SMTP 설정 사용)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# 로컬은 HTTPS 미사용
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
