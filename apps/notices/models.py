"""공지사항 모델"""
from django.conf import settings
from django.db import models


class Notice(models.Model):
    """공지사항 (운영자만 작성/수정)"""

    title: str = models.CharField(max_length=200, verbose_name='제목')
    content: str = models.TextField(verbose_name='내용')

    is_active: bool = models.BooleanField(
        default=True,
        verbose_name='활성화',
        help_text='체크 시 메인 페이지에 표시',
    )
    is_pinned: bool = models.BooleanField(
        default=False,
        verbose_name='상단 고정',
        help_text='체크 시 항상 가장 위에 표시',
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notices',
        verbose_name='작성자',
    )

    view_count: int = models.IntegerField(default=0, verbose_name='조회수')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '공지사항'
        verbose_name_plural = '공지사항 목록'
        # 정렬: 고정 글 먼저, 그 다음 최신순
        ordering = ['-is_pinned', '-created_at']

    def __str__(self) -> str:
        return self.title
