from datetime import datetime
from typing import List, Dict, Optional
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from .models import CodeReview, ReviewComment, ReviewStatus


class CodeReviewService:
    """Service class for managing code review operations and display logic."""
    
    def __init__(self, user: User):
        self.user = user
        self.review_status = ReviewStatus.PENDING
    
    def create_review(self, title: str, description: str, code_content: str) -> CodeReview:
        """Create a new code review with proper validation."""
        if not self._validate_review_data(title, description, code_content):
            raise ValidationError("Invalid review data provided")
        
        review = CodeReview.objects.create(
            title=title,
            description=description,
            code_content=code_content,
            author=self.user,
            status=self.review_status,
            created_at=timezone.now()
        )
        
        self._notify_reviewers(review)
        return review
    
    def get_user_reviews(self, include_archived: bool = False) -> QuerySet[CodeReview]:
        """Retrieve all reviews for the current user with filtering options."""
        queryset = CodeReview.objects.filter(author=self.user)
        
        if not include_archived:
            queryset = queryset.exclude(status=ReviewStatus.ARCHIVED)
        
        return queryset.order_by('-created_at')
    
    def format_review_summary(self, review: CodeReview) -> Dict[str, str]:
        """Format review data for display in user interface."""
        comments_count = self._get_comments_count(review)
        
        return {
            'id': str(review.id),
            'title': review.title,
            'status': review.get_status_display(),
            'author': review.author.get_full_name() or review.author.username,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'comments_count': str(comments_count),
            'description_preview': self._truncate_description(review.description)
        }
    
    def get_review_timeline(self, review_id: int) -> List[Dict[str, str]]:
        """Generate timeline of events for a specific review."""
        try:
            review = CodeReview.objects.get(id=review_id, author=self.user)
        except CodeReview.DoesNotExist:
            return []
        
        timeline_events = []
        
        timeline_events.append({
            'event_type': 'created',
            'timestamp': review.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'description': f'Review created by {review.author.username}'
        })
        
        comments = ReviewComment.objects.filter(review=review).order_by('created_at')
        for comment in comments:
            timeline_events.append({
                'event_type': 'comment',
                'timestamp': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'description': f'Comment added by {comment.author.username}'
            })
        
        return timeline_events
    
    def _validate_review_data(self, title: str, description: str, code_content: str) -> bool:
        """Validate review input data before creation."""
        if not title or len(title.strip()) < 5:
            return False
        if not description or len(description.strip()) < 10:
            return False
        if not code_content or len(code_content.strip()) < 20:
            return False
        return True
    
    def _get_comments_count(self, review: CodeReview) -> int:
        """Get total number of comments for a review."""
        return ReviewComment.objects.filter(review=review).count()
    
    def _truncate_description(self, description: str, max_length: int = 100) -> str:
        """Truncate description for preview display."""
        if len(description) <= max_length:
            return description
        return description[:max_length].rsplit(' ', 1)[0] + '...'
    
    def _notify_reviewers(self, review: CodeReview) -> None:
        """Send notifications to potential reviewers."""
        pass