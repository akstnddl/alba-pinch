"""구인글 관리"""
from django.contrib import admin

from .models import Application, JobPost


class ApplicationInline(admin.TabularInline):
    model = Application
    extra = 0
    readonly_fields = ('applicant', 'status', 'applied_at', 'processed_at')


@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'location', 'work_date', 'hourly_wage', 'status', 'closed_at', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'employer__nickname', 'location')
    ordering = ('-created_at',)
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    inlines = [ApplicationInline]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job_post', 'applicant', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('job_post__title', 'applicant__nickname')
    ordering = ('-applied_at',)
    readonly_fields = ('job_post', 'applicant', 'applied_at', 'processed_at')