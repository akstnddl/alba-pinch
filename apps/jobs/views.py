"""구인글 뷰"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ApplicationForm, JobPostForm
from .models import Application, JobPost
from .services import (
    ApplicationError,
    accept_application,
    apply_to_job,
    reject_application,
)


def job_list(request: HttpRequest) -> HttpResponse:
    """구인글 목록 (메인 페이지)"""
    qs = JobPost.objects.select_related('employer').filter(
        status__in=[JobPost.Status.OPEN, JobPost.Status.MATCHED]
    ).annotate(application_count=Count('applications'))
    
    # 검색
    keyword: str = request.GET.get('q', '').strip()
    if keyword:
        qs = qs.filter(
            Q(title__icontains=keyword) |
            Q(location_sigungu__icontains=keyword) |
            Q(location_dong__icontains=keyword)
        )
    
    return render(request, 'jobs/list.html', {
        'job_posts': qs[:50],  # 최신 50개
        'keyword': keyword,
    })


@login_required
def job_create(request: HttpRequest) -> HttpResponse:
    """구인글 작성"""
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job_post: JobPost = form.save(commit=False)
            job_post.employer = request.user
            job_post.save()
            messages.success(request, '구인글이 등록되었습니다.')
            return redirect('jobs:detail', pk=job_post.pk)
    else:
        form = JobPostForm()
    
    return render(request, 'jobs/create.html', {'form': form})


def job_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """구인글 상세 보기"""
    job_post = get_object_or_404(
        JobPost.objects.select_related('employer'),
        pk=pk,
    )
    
    # 조회수 증가 (본인 글은 제외)
    if not request.user.is_authenticated or request.user.id != job_post.employer_id:
        JobPost.objects.filter(pk=pk).update(view_count=F('view_count') + 1)
    
    # 내가 이미 지원했는지
    my_application = None
    if request.user.is_authenticated:
        my_application = Application.objects.filter(
            job_post=job_post,
            applicant=request.user,
        ).first()
    
    is_owner: bool = (
        request.user.is_authenticated
        and request.user.id == job_post.employer_id
    )
    
    return render(request, 'jobs/detail.html', {
        'job_post': job_post,
        'my_application': my_application,
        'is_owner': is_owner,
        'form': ApplicationForm(),
    })


@login_required
def job_apply(request: HttpRequest, pk: int) -> HttpResponse:
    """지원하기"""
    job_post = get_object_or_404(JobPost, pk=pk)
    
    if request.method != 'POST':
        return redirect('jobs:detail', pk=pk)
    
    form = ApplicationForm(request.POST)
    if not form.is_valid():
        messages.error(request, '입력값을 확인해주세요.')
        return redirect('jobs:detail', pk=pk)
    
    try:
        apply_to_job(
            job_post=job_post,
            applicant=request.user,
            message=form.cleaned_data.get('message', ''),
        )
        messages.success(request, '지원이 완료되었습니다. 구인자의 응답을 기다려주세요.')
    except ApplicationError as e:
        messages.error(request, str(e))
    
    return redirect('jobs:detail', pk=pk)


@login_required
def my_posts(request: HttpRequest) -> HttpResponse:
    """내가 작성한 구인글 + 지원자 목록"""
    qs = (
        JobPost.objects
        .filter(employer=request.user)
        .prefetch_related('applications__applicant')
    )
    return render(request, 'jobs/my_posts.html', {'job_posts': qs})


@login_required
def my_applications(request: HttpRequest) -> HttpResponse:
    """내가 지원한 글 목록"""
    qs = (
        Application.objects
        .filter(applicant=request.user)
        .select_related('job_post', 'job_post__employer')
    )
    return render(request, 'jobs/my_applications.html', {'applications': qs})


@login_required
def application_accept(request: HttpRequest, pk: int) -> HttpResponse:
    """지원 수락 (전화번호 공개)"""
    application = get_object_or_404(
        Application.objects.select_related('job_post'),
        pk=pk,
    )
    
    if request.method != 'POST':
        return redirect('jobs:my_posts')
    
    try:
        accept_application(application, request.user)
        messages.success(request, '지원자를 수락했습니다. 전화번호가 공개되었습니다.')
    except ApplicationError as e:
        messages.error(request, str(e))
    
    return redirect('jobs:my_posts')


@login_required
def application_reject(request: HttpRequest, pk: int) -> HttpResponse:
    """지원 거절"""
    application = get_object_or_404(
        Application.objects.select_related('job_post'),
        pk=pk,
    )
    
    if request.method != 'POST':
        return redirect('jobs:my_posts')
    
    try:
        reject_application(application, request.user)
        messages.success(request, '지원자를 거절했습니다.')
    except ApplicationError as e:
        messages.error(request, str(e))
    
    return redirect('jobs:my_posts')
