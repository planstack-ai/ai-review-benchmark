from typing import List, Dict, Any, Optional
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import logging
from apps.users.models import User
from apps.notifications.models import EmailLog, BulkEmailJob

logger = logging.getLogger(__name__)


class BulkEmailService:
    
    def __init__(self):
        self.default_from_email = settings.DEFAULT_FROM_EMAIL
        self.max_retries = 3
        self.retry_delay = timedelta(minutes=5)
    
    def send_bulk_notification(
        self, 
        users: List[User], 
        subject: str, 
        template_name: str,
        context: Dict[str, Any],
        priority: str = 'normal'
    ) -> Dict[str, Any]:
        job = self._create_bulk_job(users, subject, template_name, priority)
        
        try:
            with transaction.atomic():
                results = self._process_bulk_send(users, subject, template_name, context, job)
                self._update_job_status(job, results)
                return results
        except Exception as e:
            logger.error(f"Bulk email job {job.id} failed: {str(e)}")
            job.status = 'failed'
            job.error_message = str(e)
            job.save()
            raise
    
    def _create_bulk_job(
        self, 
        users: List[User], 
        subject: str, 
        template_name: str,
        priority: str
    ) -> BulkEmailJob:
        return BulkEmailJob.objects.create(
            subject=subject,
            template_name=template_name,
            recipient_count=len(users),
            priority=priority,
            status='processing',
            created_at=timezone.now()
        )
    
    def _process_bulk_send(
        self, 
        users: List[User], 
        subject: str, 
        template_name: str,
        context: Dict[str, Any],
        job: BulkEmailJob
    ) -> Dict[str, Any]:
        successful_sends = 0
        failed_sends = 0
        
        for user in users:
            try:
                personalized_context = self._prepare_user_context(user, context)
                message_body = self._render_template(template_name, personalized_context)
                
                send_mail(
                    subject=subject,
                    message=message_body,
                    from_email=self.default_from_email,
                    recipient_list=[user.email],
                    fail_silently=False
                )
                
                self._log_email_success(user, subject, job)
                successful_sends += 1
                
            except Exception as e:
                logger.warning(f"Failed to send email to {user.email}: {str(e)}")
                self._log_email_failure(user, subject, str(e), job)
                failed_sends += 1
        
        return {
            'successful_sends': successful_sends,
            'failed_sends': failed_sends,
            'total_recipients': len(users)
        }
    
    def _prepare_user_context(self, user: User, base_context: Dict[str, Any]) -> Dict[str, Any]:
        user_context = base_context.copy()
        user_context.update({
            'user_name': user.get_full_name(),
            'user_email': user.email,
            'user_id': user.id,
            'unsubscribe_url': f"{settings.SITE_URL}/unsubscribe/{user.id}"
        })
        return user_context
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        from django.template.loader import render_to_string
        return render_to_string(template_name, context)
    
    def _log_email_success(self, user: User, subject: str, job: BulkEmailJob) -> None:
        EmailLog.objects.create(
            user=user,
            subject=subject,
            status='sent',
            bulk_job=job,
            sent_at=timezone.now()
        )
    
    def _log_email_failure(self, user: User, subject: str, error: str, job: BulkEmailJob) -> None:
        EmailLog.objects.create(
            user=user,
            subject=subject,
            status='failed',
            error_message=error,
            bulk_job=job,
            sent_at=timezone.now()
        )
    
    def _update_job_status(self, job: BulkEmailJob, results: Dict[str, Any]) -> None:
        job.successful_sends = results['successful_sends']
        job.failed_sends = results['failed_sends']
        job.status = 'completed' if results['failed_sends'] == 0 else 'partial_failure'
        job.completed_at = timezone.now()
        job.save()