"""공지사항 관리자 페이지"""
from django.contrib import admin

from .models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'is_pinned', 'author', 'created_at', 'view_count')
    list_filter = ('is_active', 'is_pinned', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-is_pinned', '-created_at')
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    fieldsets = (
        ('내용', {'fields': ('title', 'content')}),
        ('설정', {'fields': ('is_active', 'is_pinned')}),
        ('정보', {'fields': ('author', 'view_count', 'created_at', 'updated_at')}),
    )
