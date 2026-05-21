"""사용자 뷰"""
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .forms import (
    LoginForm,
    PasswordResetConfirmForm,
    PasswordResetRequestForm,
    ProfileForm,
    SignupForm,
)
from .models import User

# 자동 로그인 지속 시간: 30일 (초 단위)
AUTO_LOGIN_SECONDS = 60 * 60 * 24 * 30


def signup_view(request: HttpRequest) -> HttpResponse:
    """회원가입 + 가입 후 자동 로그인"""
    if request.user.is_authenticated:
        return redirect('jobs:list')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 가입 직후 자동 로그인
            authenticated_user = authenticate(
                request,
                phone=user.phone,
                password=form.cleaned_data['password'],
            )
            if authenticated_user:
                login(request, authenticated_user)
                request.session.set_expiry(AUTO_LOGIN_SECONDS)
            messages.success(request, '가입을 환영합니다! 🎉')
            return redirect('jobs:list')
    else:
        form = SignupForm()

    return render(request, 'users/signup.html', {'form': form})


def login_view(request: HttpRequest) -> HttpResponse:
    """로그인 + 로그인 유지 옵션"""
    if request.user.is_authenticated:
        return redirect('jobs:list')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)

            user = authenticate(request, phone=phone, password=password)
            if user is not None:
                login(request, user)
                # 자동 로그인 설정
                if remember_me:
                    request.session.set_expiry(AUTO_LOGIN_SECONDS)
                else:
                    request.session.set_expiry(0)  # 브라우저 닫으면 만료
                return redirect('jobs:list')
            else:
                form.add_error(None, '휴대폰 번호 또는 비밀번호가 바르지 않습니다')
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request: HttpRequest) -> HttpResponse:
    """로그아웃"""
    logout(request)
    messages.success(request, '로그아웃되었습니다')
    return redirect('jobs:list')


@login_required
def profile_detail(request: HttpRequest) -> HttpResponse:
    """내 프로필 보기"""
    return render(request, 'users/profile_detail.html', {'user': request.user})


@login_required
def profile_edit(request: HttpRequest) -> HttpResponse:
    """프로필 수정 (닉네임, 이메일, 경력)"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 저장되었습니다')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'users/profile_edit.html', {'form': form})


# ============================================
# 비밀번호 찾기 (이메일 인증 방식)
# ============================================

def password_reset_request(request: HttpRequest) -> HttpResponse:
    """비밀번호 찾기 - 이메일 입력 페이지"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # 사용자 찾기 (없어도 동일 메시지 - 보안)
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # 이메일 노출 방지: 항상 같은 페이지로 이동
                return redirect('users:password_reset_done')

            # 토큰 생성
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(
                reverse('users:password_reset_confirm', kwargs={
                    'uidb64': uid,
                    'token': token,
                })
            )

            # 이메일 발송
            subject = '[알바핀치] 비밀번호 재설정 안내'
            message = (
                f'안녕하세요, {user.nickname}님!\n\n'
                f'비밀번호 재설정을 요청하셨습니다.\n'
                f'아래 링크를 클릭하여 새 비밀번호를 설정해주세요.\n\n'
                f'{reset_url}\n\n'
                f'⚠️ 이 링크는 24시간 동안만 유효합니다.\n'
                f'본인이 요청하지 않은 경우 이 메일을 무시해주세요.\n\n'
                f'알바핀치 드림'
            )

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception:
                # 발송 실패해도 사용자에게는 동일 메시지 (이메일 노출 방지)
                pass

            return redirect('users:password_reset_done')
    else:
        form = PasswordResetRequestForm()

    return render(request, 'users/password_reset.html', {'form': form})


def password_reset_done(request: HttpRequest) -> HttpResponse:
    """비밀번호 찾기 - 발송 완료 안내"""
    return render(request, 'users/password_reset_done.html')


def password_reset_confirm(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    """비밀번호 찾기 - 새 비번 설정 (이메일 링크로 접근)"""
    # uid 디코딩하여 사용자 찾기
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # 토큰 검증
    if user is None or not default_token_generator.check_token(user, token):
        return render(request, 'users/password_reset_invalid.html')

    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, '비밀번호가 변경되었습니다. 새 비밀번호로 로그인해주세요.')
            return redirect('users:login')
    else:
        form = PasswordResetConfirmForm()

    return render(request, 'users/password_reset_confirm.html', {
        'form': form,
        'user': user,
    })
