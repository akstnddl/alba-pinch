"""휴대폰 번호 기반 인증 백엔드"""
from typing import Optional

from django.contrib.auth.backends import BaseBackend
from django.http import HttpRequest

from .models import User


class PhoneBackend(BaseBackend):
    """휴대폰 번호 + 비밀번호로 인증"""
    
    def authenticate(
        self,
        request: Optional[HttpRequest] = None,
        phone: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs,
    ) -> Optional[User]:
        if not phone or not password:
            return None
        
        # 입력값 정리 (하이픈/공백 제거)
        phone = phone.replace('-', '').replace(' ', '')
        
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None
        
        # 비밀번호 검증 + 활성 상태 체크
        if user.check_password(password) and user.is_active and not user.is_banned:
            return user
        return None
    
    def get_user(self, user_id: int) -> Optional[User]:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
