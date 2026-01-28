from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.db import transaction
from celery import current_app
from celery.result import AsyncResult
import logging
import json

logger = logging.getLogger(__name__)


class CodeReviewBenchmarkService:
    """Service for managing AI code review benchmark operations."""
    
    def __init__(self):
        self.celery_app = current_app
        self.max_retries = getattr(settings, 'BENCHMARK_MAX_RETRIES', 3)
        self.retry_delay = getattr(settings, 'BENCHMARK_RETRY_DELAY', 60)
    
    def submit_code_for_review(self, code_snippet: str, user_id: int, 
                              benchmark_type: str = 'security') -> Dict[str, Any]:
        """Submit code snippet for AI review analysis."""
        task_data = {
            'code_snippet': code_snippet,
            'user_id': user_id,
            'benchmark_type': benchmark_type,
            'submitted_at': timezone.now().isoformat(),
        }
        
        try:
            result = self._execute_review_task(task_data)
            return {
                'task_id': result.id,
                'status': 'submitted',
                'estimated_completion': self._calculate_eta(benchmark_type)
            }
        except Exception as e:
            logger.error(f"Failed to submit review task: {str(e)}")
            return {'error': 'Failed to submit code for review'}
    
    def get_review_status(self, task_id: str) -> Dict[str, Any]:
        """Get the current status of a review task."""
        try:
            result = AsyncResult(task_id, app=self.celery_app)
            
            if result.ready():
                if result.successful():
                    return {
                        'status': 'completed',
                        'result': result.result,
                        'completed_at': timezone.now().isoformat()
                    }
                else:
                    return {
                        'status': 'failed',
                        'error': str(result.info) if result.info else 'Unknown error'
                    }
            else:
                return {
                    'status': 'processing',
                    'progress': self._get_task_progress(result)
                }
        except Exception as e:
            logger.warning(f"Could not retrieve task status: {str(e)}")
            return {'status': 'unknown', 'error': 'Task not found'}
    
    def _execute_review_task(self, task_data: Dict[str, Any]) -> AsyncResult:
        """Execute the code review task asynchronously."""
        from .tasks import analyze_code_benchmark
        
        return analyze_code_benchmark.apply_async(
            args=[task_data],
            retry=True,
            retry_policy={
                'max_retries': self.max_retries,
                'interval_start': self.retry_delay,
                'interval_step': 30,
                'interval_max': 300,
            }
        )
    
    def _calculate_eta(self, benchmark_type: str) -> str:
        """Calculate estimated time of completion based on benchmark type."""
        eta_minutes = {
            'security': 5,
            'performance': 8,
            'maintainability': 12,
            'comprehensive': 20
        }.get(benchmark_type, 10)
        
        eta_time = timezone.now() + timezone.timedelta(minutes=eta_minutes)
        return eta_time.isoformat()
    
    def _get_task_progress(self, result: AsyncResult) -> Optional[Dict[str, Any]]:
        """Extract progress information from task result."""
        try:
            if hasattr(result, 'info') and isinstance(result.info, dict):
                return result.info.get('progress', {'percent': 0})
            return {'percent': 0}
        except Exception:
            return None
    
    def _notify_completion(self, user_id: int, task_id: str, success: bool):
        """Send notification email about task completion."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
            subject = f"Code Review {'Completed' if success else 'Failed'}"
            message = f"Your code review task {task_id} has {'completed successfully' if success else 'failed'}."
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")