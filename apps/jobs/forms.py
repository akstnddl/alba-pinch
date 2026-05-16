"""구인글 폼"""
from django import forms

from .models import JobPost


class JobPostForm(forms.ModelForm):
    """구인글 작성/수정"""
    
    class Meta:
        model = JobPost
        fields = [
            'title', 'description',
            'location_sido', 'location_sigungu', 'location_dong', 'location_detail',
            'work_date', 'work_hours', 'hourly_wage',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '예: 카페 대타 급구!',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': '업무 내용, 주의사항 등 자세히 작성해주세요',
            }),
            'location_sido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '서울특별시',
            }),
            'location_sigungu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '강남구',
            }),
            'location_dong': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '역삼동',
            }),
            'location_detail': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '역삼역 5번 출구 도보 5분',
            }),
            'work_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'work_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': '0.5',
                'max': '24',
                'placeholder': '4',
            }),
            'hourly_wage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '100',
                'min': '0',
                'placeholder': '12000',
            }),
        }
        labels = {
            'title': '제목',
            'description': '상세 설명',
            'location_sido': '시/도',
            'location_sigungu': '시/군/구',
            'location_dong': '동/읍/면 (선택)',
            'location_detail': '상세 위치 (선택)',
            'work_date': '근무 시작 일시',
            'work_hours': '근무 시간 (시간 단위)',
            'hourly_wage': '시급 (원)',
        }


class ApplicationForm(forms.Form):
    """지원 메시지 폼"""
    message = forms.CharField(
        max_length=300,
        required=False,
        label='지원 메시지 (선택)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': '간단한 자기소개나 어필 포인트를 적어주세요',
        }),
    )
