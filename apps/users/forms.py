"""사용자 폼"""
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User


def normalize_phone(phone: str) -> str:
    """휴대폰 번호 정규화 (하이픈, 공백 제거)"""
    return phone.replace('-', '').replace(' ', '').strip()


class SignupForm(forms.Form):
    """회원가입 폼"""

    phone = forms.CharField(
        max_length=13,
        label='휴대폰 번호',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '01012345678',
            'inputmode': 'numeric',
            'autocomplete': 'tel',
        }),
    )
    nickname = forms.CharField(
        max_length=20,
        label='닉네임',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '다른 사용자에게 보여질 이름',
            'autocomplete': 'nickname',
        }),
    )
    # 이메일 필드 (선택, 비번 찾기에 사용)
    email = forms.EmailField(
        required=False,
        label='이메일 (선택, 비밀번호 찾기에 사용)',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@naver.com',
            'autocomplete': 'email',
        }),
        help_text='⚠️ 네이버 메일을 권장합니다. 다른 메일은 스팸함으로 갈 수 있어요.',
    )
    password = forms.CharField(
        label='비밀번호 (8자 이상)',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호',
            'autocomplete': 'new-password',
        }),
    )
    password_confirm = forms.CharField(
        label='비밀번호 확인',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호 다시 입력',
            'autocomplete': 'new-password',
        }),
    )
    career_summary = forms.CharField(
        max_length=500,
        required=False,
        label='경력 요약 (선택)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': '예: 카페 알바 6개월, 편의점 1년',
        }),
    )

    def clean_phone(self) -> str:
        phone = normalize_phone(self.cleaned_data['phone'])
        if not phone.startswith('01') or not phone.isdigit() or len(phone) < 10:
            raise ValidationError('올바른 휴대폰 번호가 아닙니다 (예: 01012345678)')
        if User.objects.filter(phone=phone).exists():
            raise ValidationError('이미 가입된 휴대폰 번호입니다')
        return phone

    def clean_nickname(self) -> str:
        nickname = self.cleaned_data['nickname'].strip()
        if len(nickname) < 2:
            raise ValidationError('닉네임은 2자 이상이어야 합니다')
        if User.objects.filter(nickname=nickname).exists():
            raise ValidationError('이미 사용 중인 닉네임입니다')
        return nickname

    def clean_email(self):
        """이메일 중복 체크 (입력한 경우만)"""
        email = self.cleaned_data.get('email', '')
        if not email:
            return None
        email = email.strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError('이미 가입된 이메일입니다')
        return email

    def clean_password(self) -> str:
        password = self.cleaned_data['password']
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError(e.messages)
        return password

    def clean(self) -> dict:
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', '비밀번호가 일치하지 않습니다')
        return cleaned_data

    def save(self) -> User:
        """가입 처리"""
        return User.objects.create_user(
            phone=self.cleaned_data['phone'],
            password=self.cleaned_data['password'],
            nickname=self.cleaned_data['nickname'],
            email=self.cleaned_data.get('email'),
            career_summary=self.cleaned_data.get('career_summary', ''),
        )


class LoginForm(forms.Form):
    """로그인 폼"""

    phone = forms.CharField(
        max_length=13,
        label='휴대폰 번호',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '01012345678',
            'inputmode': 'numeric',
            'autocomplete': 'tel',
        }),
    )
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'current-password',
        }),
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        label='로그인 유지 (30일)',
    )

    def clean_phone(self) -> str:
        return normalize_phone(self.cleaned_data['phone'])


class ProfileForm(forms.ModelForm):
    """프로필 수정 폼 - 이메일 추가/변경 가능"""

    class Meta:
        model = User
        fields = ['nickname', 'email', 'career_summary']
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@naver.com',
            }),
            'career_summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'nickname': '닉네임',
            'email': '이메일 (비밀번호 찾기에 사용)',
            'career_summary': '경력 요약',
        }
        help_texts = {
            'email': '⚠️ 네이버 메일 권장 (다른 메일은 스팸함 확인 필요)',
        }

    def clean_nickname(self) -> str:
        nickname = self.cleaned_data['nickname'].strip()
        qs = User.objects.filter(nickname=nickname)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('이미 사용 중인 닉네임입니다')
        return nickname

    def clean_email(self):
        """이메일 중복 체크 (본인 제외)"""
        email = self.cleaned_data.get('email', '')
        if not email:
            return None
        email = email.strip().lower()
        qs = User.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('이미 사용 중인 이메일입니다')
        return email


class PasswordResetRequestForm(forms.Form):
    """비밀번호 찾기 - 이메일 입력"""

    email = forms.EmailField(
        label='가입 시 등록한 이메일',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@naver.com',
            'autocomplete': 'email',
        }),
    )

    def clean_email(self) -> str:
        return self.cleaned_data['email'].strip().lower()


class PasswordResetConfirmForm(forms.Form):
    """비밀번호 찾기 - 새 비번 설정"""

    password1 = forms.CharField(
        label='새 비밀번호 (8자 이상)',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password',
        }),
    )
    password2 = forms.CharField(
        label='새 비밀번호 확인',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password',
        }),
    )

    def clean_password1(self) -> str:
        password = self.cleaned_data['password1']
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError(e.messages)
        return password

    def clean(self) -> dict:
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', '비밀번호가 일치하지 않습니다')
        return cleaned_data
