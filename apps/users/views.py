"""사용자 뷰"""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import LoginForm, ProfileForm, SignupForm

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
                form.add_error(None, '휴대폰 번호 또는 비밀번호가 올바르지 않습니다')
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
    """프로필 수정 (닉네임, 경력)"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 저장되었습니다')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'users/profile_edit.html', {'form': form})
