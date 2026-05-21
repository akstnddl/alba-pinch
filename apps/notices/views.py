"""공지사항 뷰"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import NoticeForm
from .models import Notice


def is_superuser(user) -> bool:
    """운영자(superuser) 권한 체크"""
    return user.is_authenticated and user.is_superuser


def notice_list(request: HttpRequest) -> HttpResponse:
    """공지사항 목록 (전체 보기, 누구나 접근)"""
    qs = Notice.objects.filter(is_active=True)
    return render(request, 'notices/list.html', {'notices': qs})


def notice_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """공지사항 상세 (누구나 접근)"""
    notice = get_object_or_404(Notice, pk=pk)

    # 조회수 증가
    Notice.objects.filter(pk=pk).update(view_count=F('view_count') + 1)

    return render(request, 'notices/detail.html', {'notice': notice})


@login_required
@user_passes_test(is_superuser)
def notice_manage(request: HttpRequest) -> HttpResponse:
    """공지사항 관리 페이지 (운영자 전용, 비활성화 글도 표시)"""
    qs = Notice.objects.all()
    return render(request, 'notices/manage.html', {'notices': qs})


@login_required
@user_passes_test(is_superuser)
def notice_create(request: HttpRequest) -> HttpResponse:
    """공지사항 작성 (운영자 전용)"""
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice: Notice = form.save(commit=False)
            notice.author = request.user
            notice.save()
            messages.success(request, '공지사항이 등록되었습니다.')
            return redirect('notices:manage')
    else:
        form = NoticeForm()

    return render(request, 'notices/form.html', {
        'form': form,
        'is_update': False,
    })


@login_required
@user_passes_test(is_superuser)
def notice_update(request: HttpRequest, pk: int) -> HttpResponse:
    """공지사항 수정 (운영자 전용)"""
    notice = get_object_or_404(Notice, pk=pk)

    if request.method == 'POST':
        form = NoticeForm(request.POST, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, '공지사항이 수정되었습니다.')
            return redirect('notices:manage')
    else:
        form = NoticeForm(instance=notice)

    return render(request, 'notices/form.html', {
        'form': form,
        'notice': notice,
        'is_update': True,
    })


@login_required
@user_passes_test(is_superuser)
def notice_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """공지사항 삭제 (운영자 전용)"""
    notice = get_object_or_404(Notice, pk=pk)

    if request.method == 'POST':
        title = notice.title
        notice.delete()
        messages.success(request, f'"{title}" 공지사항이 삭제되었습니다.')
        return redirect('notices:manage')

    return render(request, 'notices/confirm_delete.html', {'notice': notice})
