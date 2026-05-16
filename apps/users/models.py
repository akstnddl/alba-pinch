"""사용자 모델 - 휴대폰 번호 기반 인증"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models


phone_validator = RegexValidator(
    regex=r'^01[0-9]{8,9}$',
    message='올바른 휴대폰 번호 형식이 아닙니다 (예: 01012345678)',
)


class UserManager(BaseUserManager):
    """휴대폰 번호 기반 사용자 매니저"""
    
    def create_user(self, phone: str, password: str, nickname: str, **extra_fields):
        """일반 사용자 생성"""
        if not phone:
            raise ValueError('휴대폰 번호는 필수입니다')
        if not nickname:
            raise ValueError('닉네임은 필수입니다')
        
        user = self.model(phone=phone, nickname=nickname, **extra_fields)
        user.set_password(password)  # 비밀번호 자동 해싱
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone: str, password: str, nickname: str, **extra_fields):
        """관리자 계정 생성"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(phone, password, nickname, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """휴대폰 번호로 로그인하는 사용자"""
    
    phone: str = models.CharField(
        max_length=11,
        unique=True,
        validators=[phone_validator],
        verbose_name='휴대폰 번호',
    )
    nickname: str = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='닉네임',
    )
    career_summary: str = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='경력 요약',
    )
    
    # 평점 시스템
    rating_avg: float = models.FloatField(default=0.0)
    rating_count: int = models.IntegerField(default=0)
    
    # 권한/상태
    is_active: bool = models.BooleanField(default=True)
    is_staff: bool = models.BooleanField(default=False)
    is_banned: bool = models.BooleanField(default=False, verbose_name='이용 정지')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phone'  # 로그인 시 사용할 필드
    REQUIRED_FIELDS = ['nickname']  # createsuperuser 시 추가 입력 필드
    
    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자 목록'
    
    def __str__(self) -> str:
        return f'{self.nickname} ({self.masked_phone})'
    
    @property
    def masked_phone(self) -> str:
        """마스킹된 휴대폰 번호 (다른 사용자에게 보여줄 때)"""
        if not self.phone or len(self.phone) < 8:
            return '미등록'
        return f'{self.phone[:3]}-****-{self.phone[-4:]}'
