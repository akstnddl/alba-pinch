"""평점 + 신고"""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """매칭 완료 후 상호 평가"""
    
    job_post = models.ForeignKey('jobs.JobPost', on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    reviewee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received')
    
    rating: int = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment: str = models.TextField(max_length=300, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '평가'
        verbose_name_plural = '평가 목록'
        constraints = [
            models.UniqueConstraint(
                fields=['job_post', 'reviewer', 'reviewee'],
                name='unique_review_per_match',
            ),
        ]
    
    def __str__(self) -> str:
        return f'{self.reviewer.nickname} → {self.reviewee.nickname} ({self.rating}점)'


class Report(models.Model):
    """신고"""
    
    class Reason(models.TextChoices):
        SPAM = 'spam', '스팸/광고'
        FRAUD = 'fraud', '사기/허위'
        INAPPROPRIATE = 'inappropriate', '부적절한 내용'
        OTHER = 'other', '기타'
    
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made')
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_received', null=True, blank=True)
    target_post = models.ForeignKey('jobs.JobPost', on_delete=models.CASCADE, null=True, blank=True)
    
    reason: str = models.CharField(max_length=20, choices=Reason.choices)
    detail: str = models.TextField()
    
    is_handled: bool = models.BooleanField(default=False)
    admin_memo: str = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '신고'
        verbose_name_plural = '신고 목록'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f'[{self.get_reason_display()}]'
