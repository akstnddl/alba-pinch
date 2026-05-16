"""구인글 + 지원 모델"""
from django.conf import settings
from django.db import models


class JobPost(models.Model):
    """구인글 (대타/단기알바)"""
    
    class Status(models.TextChoices):
        OPEN = 'open', '모집중'
        MATCHED = 'matched', '매칭완료'
        CLOSED = 'closed', '마감'
        CANCELLED = 'cancelled', '취소'
    
    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_posts',
        verbose_name='구인자',
    )
    
    title: str = models.CharField(max_length=100, verbose_name='제목')
    description: str = models.TextField(verbose_name='상세 설명')
    
    location_sido: str = models.CharField(max_length=20, verbose_name='시/도')
    location_sigungu: str = models.CharField(max_length=20, verbose_name='시/군/구')
    location_dong: str = models.CharField(max_length=30, blank=True, verbose_name='동/읍/면')
    location_detail: str = models.CharField(max_length=100, blank=True, verbose_name='상세 위치')
    
    work_date = models.DateTimeField(verbose_name='근무 시작 일시')
    work_hours: float = models.FloatField(verbose_name='근무 시간')
    hourly_wage: int = models.IntegerField(verbose_name='시급 (원)')
    
    status: str = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name='상태',
    )
    
    view_count: int = models.IntegerField(default=0, verbose_name='조회수')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '구인글'
        verbose_name_plural = '구인글 목록'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['location_sigungu', 'status']),
            models.Index(fields=['work_date']),
        ]
    
    def __str__(self) -> str:
        return f'[{self.location_sigungu}] {self.title}'
    
    @property
    def total_wage(self) -> int:
        return int(self.hourly_wage * self.work_hours)
    
    @property
    def is_open(self) -> bool:
        return self.status == self.Status.OPEN


class Application(models.Model):
    """지원"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', '대기중'
        ACCEPTED = 'accepted', '수락됨'
        REJECTED = 'rejected', '거절됨'
        CANCELLED = 'cancelled', '지원취소'
    
    job_post = models.ForeignKey(
        JobPost,
        on_delete=models.CASCADE,
        related_name='applications',
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
    )
    message: str = models.TextField(max_length=300, blank=True, verbose_name='지원 메시지')
    status: str = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = '지원'
        verbose_name_plural = '지원 목록'
        ordering = ['-applied_at']
        constraints = [
            models.UniqueConstraint(
                fields=['job_post', 'applicant'],
                name='unique_application_per_post',
            ),
        ]
    
    def __str__(self) -> str:
        return f'{self.applicant.nickname} → {self.job_post.title} ({self.get_status_display()})'
    
    @property
    def is_phone_revealed(self) -> bool:
        return self.status == self.Status.ACCEPTED
