"""구인/지원 비즈니스 로직"""
from django.db import transaction
from django.utils import timezone

from .models import Application, JobPost


class ApplicationError(Exception):
    """지원 관련 예외"""
    pass


@transaction.atomic
def apply_to_job(job_post: JobPost, applicant, message: str = '') -> Application:
    """구인글에 지원"""
    if job_post.employer_id == applicant.id:
        raise ApplicationError('본인이 작성한 구인글에는 지원할 수 없습니다.')
    
    if not job_post.is_open:
        raise ApplicationError('모집이 마감된 구인글입니다.')
    
    if applicant.is_banned:
        raise ApplicationError('이용이 정지된 계정입니다.')
    
    if Application.objects.filter(job_post=job_post, applicant=applicant).exists():
        raise ApplicationError('이미 지원한 구인글입니다.')
    
    return Application.objects.create(
        job_post=job_post,
        applicant=applicant,
        message=message,
    )


@transaction.atomic
def accept_application(application: Application, requester) -> Application:
    """
    지원 수락
    
    - 해당 지원 → 수락됨 (전화번호 공개)
    - 구인글 → 매칭완료
    - 같은 글의 다른 대기중 지원 → 자동 거절
    """
    if application.job_post.employer_id != requester.id:
        raise ApplicationError('본인이 작성한 구인글의 지원자만 수락할 수 있습니다.')
    
    if application.status != Application.Status.PENDING:
        raise ApplicationError(f'이미 처리된 지원입니다 ({application.get_status_display()}).')
    
    application.status = Application.Status.ACCEPTED
    application.processed_at = timezone.now()
    application.save()
    
    job_post = application.job_post
    job_post.status = JobPost.Status.MATCHED
    job_post.save()
    
    # 같은 글의 다른 대기중 지원은 자동 거절
    Application.objects.filter(
        job_post=job_post,
        status=Application.Status.PENDING,
    ).exclude(id=application.id).update(
        status=Application.Status.REJECTED,
        processed_at=timezone.now(),
    )
    
    return application


@transaction.atomic
def reject_application(application: Application, requester) -> Application:
    """지원 거절"""
    if application.job_post.employer_id != requester.id:
        raise ApplicationError('본인이 작성한 구인글의 지원자만 거절할 수 있습니다.')
    
    if application.status != Application.Status.PENDING:
        raise ApplicationError(f'이미 처리된 지원입니다 ({application.get_status_display()}).')
    
    application.status = Application.Status.REJECTED
    application.processed_at = timezone.now()
    application.save()
    return application
