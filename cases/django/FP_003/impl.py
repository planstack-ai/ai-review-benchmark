from typing import List, Optional, Dict, Any
from decimal import Decimal
from django.db import transaction
from django.db.models import QuerySet, Q, Count, Avg, Sum
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import CodeReview, ReviewMetric, Reviewer


class CodeReviewBenchmarkService:
    
    def __init__(self):
        self.default_metrics = ['complexity', 'maintainability', 'security', 'performance']
    
    def get_reviews_by_status(self, status: str) -> QuerySet[CodeReview]:
        return CodeReview.objects.filter(status=status).select_related('reviewer')
    
    def get_pending_reviews(self, reviewer_id: Optional[int] = None) -> QuerySet[CodeReview]:
        queryset = CodeReview.objects.filter(status='pending')
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        return queryset.order_by('created_at')
    
    def calculate_reviewer_statistics(self, reviewer_id: int, days: int = 30) -> Dict[str, Any]:
        cutoff_date = timezone.now() - timedelta(days=days)
        
        reviews = CodeReview.objects.filter(
            reviewer_id=reviewer_id,
            completed_at__gte=cutoff_date
        ).aggregate(
            total_reviews=Count('id'),
            avg_score=Avg('overall_score'),
            total_lines_reviewed=Sum('lines_of_code')
        )
        
        return {
            'reviewer_id': reviewer_id,
            'period_days': days,
            'total_reviews': reviews['total_reviews'] or 0,
            'average_score': reviews['avg_score'] or Decimal('0.00'),
            'total_lines_reviewed': reviews['total_lines_reviewed'] or 0
        }
    
    def get_high_priority_reviews(self, min_complexity: int = 8) -> QuerySet[CodeReview]:
        return CodeReview.objects.filter(
            Q(priority='high') | Q(complexity_score__gte=min_complexity),
            status__in=['pending', 'in_progress']
        ).select_related('reviewer').prefetch_related('metrics')
    
    @transaction.atomic
    def assign_review_batch(self, reviewer_id: int, max_reviews: int = 5) -> List[CodeReview]:
        reviewer = Reviewer.objects.select_for_update().get(id=reviewer_id)
        
        if not self._can_assign_reviews(reviewer, max_reviews):
            raise ValidationError(f"Reviewer {reviewer_id} cannot be assigned more reviews")
        
        pending_reviews = self._get_assignable_reviews(max_reviews)
        assigned_reviews = []
        
        for review in pending_reviews:
            review.reviewer = reviewer
            review.status = 'assigned'
            review.assigned_at = timezone.now()
            review.save()
            assigned_reviews.append(review)
        
        return assigned_reviews
    
    def get_benchmark_metrics(self, project_id: Optional[int] = None) -> Dict[str, Decimal]:
        queryset = ReviewMetric.objects.all()
        if project_id:
            queryset = queryset.filter(review__project_id=project_id)
        
        metrics = {}
        for metric_type in self.default_metrics:
            avg_value = queryset.filter(metric_type=metric_type).aggregate(
                avg_score=Avg('score')
            )['avg_score']
            metrics[metric_type] = avg_value or Decimal('0.00')
        
        return metrics
    
    def _can_assign_reviews(self, reviewer: Reviewer, requested_count: int) -> bool:
        current_assigned = CodeReview.objects.filter(
            reviewer=reviewer,
            status__in=['assigned', 'in_progress']
        ).count()
        
        return current_assigned + requested_count <= reviewer.max_concurrent_reviews
    
    def _get_assignable_reviews(self, limit: int) -> QuerySet[CodeReview]:
        return CodeReview.objects.filter(
            status='pending',
            reviewer__isnull=True
        ).order_by('priority', 'created_at')[:limit]