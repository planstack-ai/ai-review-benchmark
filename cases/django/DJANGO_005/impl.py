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
            'performance': Decimal('0.2'),
            'style': Decimal('0.1')
        }
    
    def submit_review_for_benchmark(
        self, 
        reviewer_id: int, 
        code_snippet: str, 
        review_data: Dict[str, Any]
    ) -> ReviewResult:
        """Submit a code review for benchmarking evaluation."""
        
        with transaction.atomic():
            reviewer = self._get_reviewer(reviewer_id)
            
            code_review = self._create_code_review(
                reviewer=reviewer,
                code_snippet=code_snippet,
                review_data=review_data
            )
            
            benchmark_score = self._calculate_benchmark_score(review_data)
            
            review_result = self._create_review_result(
                code_review=code_review,
                benchmark_score=benchmark_score,
                review_data=review_data
            )
            
            self._update_reviewer_stats(reviewer, benchmark_score)
            
            send_review_notification_task.delay(
                reviewer_id=reviewer.id,
                review_result_id=review_result.id,
                score=float(benchmark_score)
            )
            
            update_metrics_task.delay(
                review_type='benchmark',
                score=float(benchmark_score),
                reviewer_id=reviewer.id
            )
            
            return review_result
    
    def _get_reviewer(self, reviewer_id: int) -> User:
        """Retrieve and validate reviewer."""
        try:
            return User.objects.get(id=reviewer_id, is_active=True)
        except User.DoesNotExist:
            raise ValidationError(f"Reviewer with id {reviewer_id} not found")
    
    def _create_code_review(
        self, 
        reviewer: User, 
        code_snippet: str, 
        review_data: Dict[str, Any]
    ) -> CodeReview:
        """Create a new code review record."""
        
        if len(code_snippet.strip()) < 10:
            raise ValidationError("Code snippet too short for meaningful review")
        
        return CodeReview.objects.create(
            reviewer=reviewer,
            code_snippet=code_snippet,
            review_comments=review_data.get('comments', ''),
            issues_found=review_data.get('issues', []),
            suggestions=review_data.get('suggestions', []),
            submitted_at=timezone.now()
        )
    
    def _calculate_benchmark_score(self, review_data: Dict[str, Any]) -> Decimal:
        """Calculate weighted benchmark score based on review quality metrics."""
        
        accuracy_score = self._evaluate_accuracy(review_data)
        completeness_score = self._evaluate_completeness(review_data)
        performance_score = self._evaluate_performance_insights(review_data)
        style_score = self._evaluate_style_feedback(review_data)
        
        total_score = (
            accuracy_score * self.scoring_weights['accuracy'] +
            completeness_score * self.scoring_weights['completeness'] +
            performance_score * self.scoring_weights['performance'] +
            style_score * self.scoring_weights['style']
        )
        
        return min(total_score, Decimal('100.0'))
    
    def _evaluate_accuracy(self, review_data: Dict[str, Any]) -> Decimal:
        """Evaluate accuracy of identified issues."""
        issues = review_data.get('issues', [])
        if not issues:
            return Decimal('50.0')
        
        valid_issues = sum(1 for issue in issues if issue.get('severity', 0) > 2)
        return min(Decimal(str(valid_issues * 20)), Decimal('100.0'))
    
    def _evaluate_completeness(self, review_data: Dict[str, Any]) -> Decimal:
        """Evaluate completeness of the review."""
        completeness_factors = [
            bool(review_data.get('comments')),
            bool(review_data.get('issues')),
            bool(review_data.get('suggestions')),
            len(review_data.get('comments', '')) > 50
        ]
        
        score = sum(completeness_factors) * 25
        return Decimal(str(score))
    
    def _evaluate_performance_insights(self, review_data: Dict[str, Any]) -> Decimal:
        """Evaluate quality of performance-related feedback."""
        performance_keywords = ['performance', 'optimization', 'efficiency', 'complexity']
        comments = review_data.get('comments', '').lower()
        
        keyword_matches = sum(1 for keyword in performance_keywords if keyword in comments)
        return min(Decimal(str(keyword_matches * 30)), Decimal('100.0'))
    
    def _evaluate_style_feedback(self, review_data: Dict[str, Any]) -> Decimal:
        """Evaluate quality of style and convention feedback."""
        style_keywords = ['pep8', 'naming', 'convention', 'readability', 'style']
        comments = review_data.get('comments', '').lower()
        
        keyword_matches = sum(1 for keyword in style_keywords if keyword in comments)
        return min(Decimal(str(keyword_matches * 25)), Decimal('100.0'))
    
    def _create_review_result(
        self, 
        code_review: CodeReview, 
        benchmark_score: Decimal, 
        review_data: Dict[str, Any]
    ) -> ReviewResult:
        """Create benchmark result record."""
        
        return ReviewResult.objects.create(
            code_review=code_review,
            benchmark_score=benchmark_score,
            accuracy_score=self._evaluate_accuracy(review_data),
            completeness_score=self._evaluate_completeness(review_data),
            performance_score=self._evaluate_performance_insights(review_data),
            style_score=self._evaluate_style_feedback(review_data),
            evaluated_at=timezone.now()
        )
    
    def _update_reviewer_stats(self, reviewer: User, score: Decimal) -> None:
        """Update reviewer's benchmark statistics."""
        
        profile = reviewer.profile
        profile.total_reviews += 1
        profile.average_score = (
            (profile.average_score * (profile.total_reviews - 1) + score) / 
            profile.total_reviews
        )
        profile.last_review_date = timezone.now()
        profile.save()