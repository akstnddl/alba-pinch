"""공지사항 URL"""
from django.urls import path

from . import views

app_name = 'notices'

urlpatterns = [
    path('', views.notice_list, name='list'),
    path('manage/', views.notice_manage, name='manage'),
    path('new/', views.notice_create, name='create'),
    path('<int:pk>/', views.notice_detail, name='detail'),
    path('<int:pk>/edit/', views.notice_update, name='update'),
    path('<int:pk>/delete/', views.notice_delete, name='delete'),
]
