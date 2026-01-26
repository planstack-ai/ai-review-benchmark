from decimal import Decimal
from typing import Optional, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from myapp.models import CodeReview, ReviewResult, User
from myapp.tasks import send_review_notification_task, update_metrics_task
import logging

logger = logging.getLogger(__name__)


class CodeReviewBenchmarkService:
    """Service for managing AI code review benchmarks and scoring."""
    
    def __init__(self):
        self.scoring_weights = {
            'accuracy': Decimal('0.4'),
            'completeness': Decimal('0.3'),
            'response_time': Decimal('0.2'),
            'clarity': Decimal('0.1')
        }
    
    def submit_review_for_benchmark(
        self, 
        reviewer_id: int, 
        code_snippet: str, 
        review_data: Dict[str, Any]
    ) -> ReviewResult:
        """Submit a code review for benchmark evaluation."""
        
        with transaction.atomic():
            reviewer = self._get_reviewer(reviewer_id)
            
            review = self._create_review_record(
                reviewer=reviewer,
                code_snippet=code_snippet,
                review_data=review_data
            )
            
            benchmark_score = self._calculate_benchmark_score(review_data)
            
            result = ReviewResult.objects.create(
                review=review,
                benchmark_score=benchmark_score,
                submitted_at=timezone.now(),
                status='pending_validation'
            )
            
            self._update_reviewer_stats(reviewer, benchmark_score)
            
            send_review_notification_task.delay(result.id)
            update_metrics_task.delay(reviewer.id, benchmark_score)
            
            logger.info(f"Review submitted for benchmark: {result.id}")
            
            return result
    
    def _get_reviewer(self, reviewer_id: int) -> User:
        """Retrieve and validate reviewer."""
        try:
            reviewer = User.objects.select_for_update().get(id=reviewer_id)
            if not reviewer.is_active:
                raise ValidationError("Reviewer account is inactive")
            return reviewer
        except User.DoesNotExist:
            raise ValidationError(f"Reviewer with id {reviewer_id} not found")
    
    def _create_review_record(
        self, 
        reviewer: User, 
        code_snippet: str, 
        review_data: Dict[str, Any]
    ) -> CodeReview:
        """Create the main review record."""
        
        if len(code_snippet.strip()) < 10:
            raise ValidationError("Code snippet too short for meaningful review")
        
        review = CodeReview.objects.create(
            reviewer=reviewer,
            code_snippet=code_snippet,
            findings=review_data.get('findings', []),
            suggestions=review_data.get('suggestions', []),
            severity_assessment=review_data.get('severity', 'medium'),
            review_time_seconds=review_data.get('time_taken', 0)
        )
        
        return review
    
    def _calculate_benchmark_score(self, review_data: Dict[str, Any]) -> Decimal:
        """Calculate weighted benchmark score based on review quality metrics."""
        
        accuracy_score = Decimal(str(review_data.get('accuracy_score', 0.0)))
        completeness_score = Decimal(str(review_data.get('completeness_score', 0.0)))
        response_time_score = self._calculate_time_score(
            review_data.get('time_taken', 0)
        )
        clarity_score = Decimal(str(review_data.get('clarity_score', 0.0)))
        
        weighted_score = (
            accuracy_score * self.scoring_weights['accuracy'] +
            completeness_score * self.scoring_weights['completeness'] +
            response_time_score * self.scoring_weights['response_time'] +
            clarity_score * self.scoring_weights['clarity']
        )
        
        return min(weighted_score, Decimal('100.0'))
    
    def _calculate_time_score(self, time_taken: int) -> Decimal:
        """Calculate score based on review completion time."""
        if time_taken <= 300:  # 5 minutes
            return Decimal('100.0')
        elif time_taken <= 600:  # 10 minutes
            return Decimal('80.0')
        elif time_taken <= 900:  # 15 minutes
            return Decimal('60.0')
        else:
            return Decimal('40.0')
    
    def _update_reviewer_stats(self, reviewer: User, score: Decimal) -> None:
        """Update reviewer's benchmark statistics."""
        
        profile = reviewer.profile
        profile.total_reviews += 1
        profile.average_score = (
            (profile.average_score * (profile.total_reviews - 1) + score) 
            / profile.total_reviews
        )
        profile.last_review_date = timezone.now()
        profile.save()