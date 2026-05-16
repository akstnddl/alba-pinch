#!/usr/bin/env python
"""Django 관리 명령 진입점"""
import os
import sys


def main() -> None:
    # 기본은 개발 환경
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            'Django가 설치되어 있지 않거나 PYTHONPATH 설정이 잘못되었습니다.'
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
