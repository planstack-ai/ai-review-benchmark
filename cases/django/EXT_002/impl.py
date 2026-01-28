from typing import Dict, Any, Optional
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import json
import logging
from .models import WebhookLog, CodeReview, Repository
from .exceptions import WebhookProcessingError

logger = logging.getLogger(__name__)


class WebhookProcessingService:
    """Service for processing incoming webhooks from code review platforms."""
    
    def __init__(self):
        self.supported_events = {
            'pull_request.opened',
            'pull_request.synchronize',
            'pull_request.closed',
            'push'
        }
    
    def process_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """Process incoming webhook payload and trigger code review analysis."""
        event_type = headers.get('X-GitHub-Event', '')
        delivery_id = headers.get('X-GitHub-Delivery', '')
        
        if not self._is_supported_event(event_type):
            logger.info(f"Unsupported event type: {event_type}")
            return False
        
        try:
            with transaction.atomic():
                webhook_log = self._create_webhook_log(
                    event_type=event_type,
                    delivery_id=delivery_id,
                    payload=payload
                )
                
                if event_type in ['pull_request.opened', 'pull_request.synchronize']:
                    return self._handle_pull_request_event(payload, webhook_log)
                elif event_type == 'push':
                    return self._handle_push_event(payload, webhook_log)
                
                return True
                
        except Exception as e:
            logger.error(f"Error processing webhook {delivery_id}: {str(e)}")
            raise WebhookProcessingError(f"Failed to process webhook: {str(e)}")
    
    def _is_supported_event(self, event_type: str) -> bool:
        """Check if the event type is supported for processing."""
        return event_type in self.supported_events
    
    def _create_webhook_log(self, event_type: str, delivery_id: str, payload: Dict[str, Any]) -> WebhookLog:
        """Create a log entry for the webhook."""
        return WebhookLog.objects.create(
            event_type=event_type,
            delivery_id=delivery_id,
            payload=json.dumps(payload),
            received_at=timezone.now(),
            status='processing'
        )
    
    def _handle_pull_request_event(self, payload: Dict[str, Any], webhook_log: WebhookLog) -> bool:
        """Handle pull request related events."""
        pr_data = payload.get('pull_request', {})
        repository_data = payload.get('repository', {})
        
        repo_full_name = repository_data.get('full_name')
        pr_number = pr_data.get('number')
        
        if not repo_full_name or not pr_number:
            webhook_log.status = 'failed'
            webhook_log.error_message = 'Missing required PR data'
            webhook_log.save()
            return False
        
        repository = self._get_or_create_repository(repository_data)
        code_review = self._create_code_review(pr_data, repository, webhook_log)
        
        webhook_log.status = 'completed'
        webhook_log.save()
        
        return True
    
    def _handle_push_event(self, payload: Dict[str, Any], webhook_log: WebhookLog) -> bool:
        """Handle push events for repository updates."""
        repository_data = payload.get('repository', {})
        commits = payload.get('commits', [])
        
        if not commits:
            webhook_log.status = 'completed'
            webhook_log.save()
            return True
        
        repository = self._get_or_create_repository(repository_data)
        
        for commit in commits:
            self._process_commit_analysis(commit, repository)
        
        webhook_log.status = 'completed'
        webhook_log.save()
        
        return True
    
    def _get_or_create_repository(self, repository_data: Dict[str, Any]) -> Repository:
        """Get or create repository from webhook data."""
        repo_id = repository_data.get('id')
        full_name = repository_data.get('full_name')
        
        repository, created = Repository.objects.get_or_create(
            external_id=repo_id,
            defaults={
                'name': repository_data.get('name', ''),
                'full_name': full_name,
                'clone_url': repository_data.get('clone_url', ''),
                'default_branch': repository_data.get('default_branch', 'main')
            }
        )
        
        return repository
    
    def _create_code_review(self, pr_data: Dict[str, Any], repository: Repository, webhook_log: WebhookLog) -> CodeReview:
        """Create a new code review entry."""
        return CodeReview.objects.create(
            repository=repository,
            pull_request_number=pr_data.get('number'),
            title=pr_data.get('title', ''),
            author=pr_data.get('user', {}).get('login', ''),
            status='pending',
            webhook_log=webhook_log
        )
    
    def _process_commit_analysis(self, commit: Dict[str, Any], repository: Repository) -> None:
        """Process individual commit for analysis."""
        commit_sha = commit.get('id')
        if commit_sha:
            logger.info(f"Processing commit {commit_sha} for repository {repository.full_name}")