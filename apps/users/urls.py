"""사용자 URL"""
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_detail, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # 비밀번호 찾기 (이메일 인증)
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path(
        'password-reset/confirm/<str:uidb64>/<str:token>/',
        views.password_reset_confirm,
        name='password_reset_confirm',
    ),
]
