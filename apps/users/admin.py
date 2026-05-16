"""사용자 관리자 페이지"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('phone', 'nickname')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('phone', 'nickname', 'career_summary', 'is_active', 'is_staff', 'is_banned')


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """휴대폰 번호 기반 사용자 관리"""
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    
    list_display = ('nickname', 'phone', 'rating_avg', 'is_banned', 'is_staff', 'created_at')
    list_filter = ('is_banned', 'is_staff', 'is_active', 'created_at')
    search_fields = ('nickname', 'phone')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('프로필', {'fields': ('nickname', 'career_summary')}),
        ('평점', {'fields': ('rating_avg', 'rating_count')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_banned', 'groups', 'user_permissions')}),
        ('일시', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'nickname', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('last_login',)
    
    actions = ['ban_users', 'unban_users']
    
    @admin.action(description='선택한 사용자 이용 정지')
    def ban_users(self, request, queryset) -> None:
        queryset.update(is_banned=True, is_active=False)
    
    @admin.action(description='선택한 사용자 이용 정지 해제')
    def unban_users(self, request, queryset) -> None:
        queryset.update(is_banned=False, is_active=True)
