"""구인글 URL"""
from django.urls import path

from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='list'),
    path('jobs/new/', views.job_create, name='create'),
    path('jobs/<int:pk>/', views.job_detail, name='detail'),
    # 신규: 수정/삭제/마감
    path('jobs/<int:pk>/edit/', views.job_update, name='update'),
    path('jobs/<int:pk>/delete/', views.job_delete, name='delete'),
    path('jobs/<int:pk>/close/', views.job_close, name='close'),
    path('jobs/<int:pk>/apply/', views.job_apply, name='apply'),
    path('jobs/my/', views.my_posts, name='my_posts'),
    path('jobs/applications/', views.my_applications, name='my_applications'),
    path('applications/<int:pk>/accept/', views.application_accept, name='accept'),
    path('applications/<int:pk>/reject/', views.application_reject, name='reject'),
    path('applications/<int:pk>/cancel-rejection/', views.application_cancel_rejection, name='cancel_rejection'),
]
