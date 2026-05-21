"""공지사항 폼"""
from django import forms

from .models import Notice


class NoticeForm(forms.ModelForm):
    """공지사항 작성/수정"""

    class Meta:
        model = Notice
        fields = ['title', 'content', 'is_active', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '공지사항 제목을 입력하세요',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': '공지사항 내용을 입력하세요',
            }),
        }
        labels = {
            'title': '제목',
            'content': '내용',
            'is_active': '활성화 (체크 시 사용자에게 표시)',
            'is_pinned': '상단 고정 (체크 시 가장 위에 표시)',
        }
