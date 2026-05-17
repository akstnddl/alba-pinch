"""구인글 뷰"""
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ApplicationForm, JobPostForm
from .models import Application, JobPost
from .services import (
    ApplicationError,
    accept_application,
    apply_to_job,
    reject_application,
)


# =============================================================
# 헬퍼: 마감 후 7일 지난 구인글 자동 삭제
#   - 별도 cron 없이 목록 조회 시마다 정리
#   - closed_at 인덱스 사용해서 DB 부담 미미
# =============================================================

def cleanup_old_closed_posts() -> int:
    """마감 후 7일 지난 구인글 자동 삭제. 삭제 건수 반환."""
    week_ago = timezone.now() - timedelta(days=7)
    deleted_count, _ = JobPost.objects.filter(
        closed_at__isnull=False,
        closed_at__lt=week_ago,
    ).delete()
    return deleted_count


def job_list(request: HttpRequest) -> HttpResponse:
    """구인글 목록 (메인 페이지)"""
    # 마감 후 7일 지난 글 자동 정리
    cleanup_old_closed_posts()

    qs = JobPost.objects.select_related('employer').filter(
        status__in=[
            JobPost.Status.OPEN,
            JobPost.Status.MATCHED,
            JobPost.Status.CLOSED,
        ]
    ).annotate(application_count=Count('applications'))

    # 검색 (장소 통합 필드로 변경)
    keyword: str = request.GET.get('q', '').strip()
    if keyword:
        qs = qs.filter(
            Q(title__icontains=keyword) |
            Q(location__icontains=keyword)
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

    return render(request, 'jobs/create.html', {
        'form': form,
        'is_update': False,
    })


@login_required
def job_update(request: HttpRequest, pk: int) -> HttpResponse:
    """구인글 수정 (작성자만)"""
    job_post = get_object_or_404(JobPost, pk=pk)

    if job_post.employer != request.user:
        messages.error(request, '본인이 작성한 구인글만 수정할 수 있습니다.')
        return redirect('jobs:detail', pk=pk)

    if job_post.status != JobPost.Status.OPEN:
        messages.error(request, '모집중인 구인글만 수정할 수 있습니다.')
        return redirect('jobs:detail', pk=pk)

    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job_post)
        if form.is_valid():
            form.save()
            messages.success(request, '구인글이 수정되었습니다.')
            return redirect('jobs:detail', pk=pk)
    else:
        form = JobPostForm(instance=job_post)

    return render(request, 'jobs/create.html', {
        'form': form,
        'job_post': job_post,
        'is_update': True,
    })


@login_required
def job_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """구인글 삭제 (작성자만)"""
    job_post = get_object_or_404(JobPost, pk=pk)

    if job_post.employer != request.user:
        messages.error(request, '본인이 작성한 구인글만 삭제할 수 있습니다.')
        return redirect('jobs:detail', pk=pk)

    if request.method == 'POST':
        title = job_post.title
        job_post.delete()
        messages.success(request, f'"{title}" 구인글이 삭제되었습니다.')
        return redirect('jobs:list')

    return render(request, 'jobs/confirm_delete.html', {
        'job_post': job_post,
    })


@login_required
@require_POST
def job_close(request: HttpRequest, pk: int) -> HttpResponse:
    """모집 마감 (작성자만, POST 전용)"""
    job_post = get_object_or_404(JobPost, pk=pk)

    if job_post.employer != request.user:
        messages.error(request, '본인이 작성한 구인글만 마감할 수 있습니다.')
        return redirect('jobs:detail', pk=pk)

    if job_post.status != JobPost.Status.OPEN:
        messages.error(request, '이미 마감된 구인글입니다.')
        return redirect('jobs:detail', pk=pk)

    job_post.status = JobPost.Status.CLOSED
    job_post.closed_at = timezone.now()
    job_post.save(update_fields=['status', 'closed_at', 'updated_at'])

    messages.success(request, '모집이 마감되었습니다. 7일 후 자동 삭제됩니다.')
    return redirect('jobs:detail', pk=pk)


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
        # 매칭 완료 시 closed_at 기록 (7일 후 자동 삭제 카운트다운 시작)
        job_post = application.job_post
        job_post.refresh_from_db()
        if job_post.status == JobPost.Status.MATCHED and not job_post.closed_at:
            job_post.closed_at = timezone.now()
            job_post.save(update_fields=['closed_at'])
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
