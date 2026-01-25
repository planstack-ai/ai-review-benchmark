from typing import List, Optional, Dict, Any
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.utils import timezone
from django.contrib.auth.models import User
from .models import CodeReview, ReviewComment, ReviewMetrics


class CodeReviewService:
    
    def __init__(self):
        self.default_metrics = {
            'complexity_score': Decimal('0.0'),
            'maintainability_score': Decimal('0.0'),
            'security_score': Decimal('0.0')
        }
    
    def create_review(self, user: User, repository_url: str, branch_name: str, 
                     commit_hash: str, **kwargs) -> CodeReview:
        with transaction.atomic():
            review_data = self._prepare_review_data(
                user, repository_url, branch_name, commit_hash, **kwargs
            )
            review = CodeReview.objects.create(**review_data)
            self._initialize_review_metrics(review)
            return review
    
    def get_review_by_id(self, review_id: int) -> Optional[CodeReview]:
        try:
            return CodeReview.objects.select_related('author', 'metrics').get(id=review_id)
        except CodeReview.DoesNotExist:
            return None
    
    def update_review_status(self, review_id: int, status: str, 
                           updated_by: User) -> Optional[CodeReview]:
        review = self.get_review_by_id(review_id)
        if not review:
            return None
        
        if not self._validate_status_transition(review.status, status):
            raise ValidationError(f"Invalid status transition from {review.status} to {status}")
        
        review.status = status
        review.updated_by = updated_by
        review.updated_at = timezone.now()
        review.save(update_fields=['status', 'updated_by', 'updated_at'])
        return review
    
    def add_comment(self, review_id: int, author: User, content: str, 
                   line_number: Optional[int] = None, file_path: Optional[str] = None) -> ReviewComment:
        review = self.get_review_by_id(review_id)
        if not review:
            raise ValidationError("Review not found")
        
        comment_data = {
            'review': review,
            'author': author,
            'content': content,
            'line_number': line_number,
            'file_path': file_path,
            'created_at': timezone.now()
        }
        return ReviewComment.objects.create(**comment_data)
    
    def get_reviews_by_user(self, user: User, status: Optional[str] = None) -> QuerySet:
        queryset = CodeReview.objects.filter(author=user).select_related('metrics')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at')
    
    def delete_review(self, review_id: int, user: User) -> bool:
        review = self.get_review_by_id(review_id)
        if not review or review.author != user:
            return False
        
        with transaction.atomic():
            ReviewComment.objects.filter(review=review).delete()
            ReviewMetrics.objects.filter(review=review).delete()
            review.delete()
        return True
    
    def _prepare_review_data(self, user: User, repository_url: str, 
                           branch_name: str, commit_hash: str, **kwargs) -> Dict[str, Any]:
        return {
            'author': user,
            'repository_url': repository_url,
            'branch_name': branch_name,
            'commit_hash': commit_hash,
            'title': kwargs.get('title', f"Review for {branch_name}"),
            'description': kwargs.get('description', ''),
            'status': kwargs.get('status', 'pending'),
            'created_at': timezone.now()
        }
    
    def _initialize_review_metrics(self, review: CodeReview) -> ReviewMetrics:
        return ReviewMetrics.objects.create(
            review=review,
            **self.default_metrics
        )
    
    def _validate_status_transition(self, current_status: str, new_status: str) -> bool:
        valid_transitions = {
            'pending': ['in_progress', 'cancelled'],
            'in_progress': ['completed', 'pending', 'cancelled'],
            'completed': ['in_progress'],
            'cancelled': ['pending']
        }
        return new_status in valid_transitions.get(current_status, [])