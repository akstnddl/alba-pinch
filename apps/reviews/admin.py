"""평가/신고 관리"""
from django.contrib import admin

from .models import Report, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewee', 'rating', 'job_post', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer__nickname', 'reviewee__nickname')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reason', 'reporter', 'target_user', 'target_post', 'is_handled', 'created_at')
    list_filter = ('reason', 'is_handled')
    search_fields = ('reporter__nickname',)
    
    actions = ['mark_handled']
    
    @admin.action(description='선택한 신고 처리 완료')
    def mark_handled(self, request, queryset) -> None:
        queryset.update(is_handled=True)
