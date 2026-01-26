from typing import List, Optional, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from .models import CodeReview, ReviewMetric, BenchmarkResult


class CodeReviewBenchmarkService:
    
    def __init__(self):
        self.default_weights = {
            'complexity': Decimal('0.3'),
            'maintainability': Decimal('0.25'),
            'performance': Decimal('0.2'),
            'security': Decimal('0.15'),
            'style': Decimal('0.1')
        }
    
    def calculate_benchmark_score(self, review_id: int) -> Dict[str, Any]:
        review = self._get_review_with_metrics(review_id)
        if not review:
            raise ValidationError(f"Review with id {review_id} not found")
        
        metrics = self._extract_metrics(review)
        weighted_score = self._calculate_weighted_score(metrics)
        grade = self._determine_grade(weighted_score)
        
        return {
            'review_id': review_id,
            'score': weighted_score,
            'grade': grade,
            'metrics': metrics,
            'timestamp': timezone.now()
        }
    
    def batch_process_reviews(self, review_ids: List[int]) -> List[Dict[str, Any]]:
        results = []
        
        with transaction.atomic():
            for review_id in review_ids:
                try:
                    result = self.calculate_benchmark_score(review_id)
                    self._save_benchmark_result(result)
                    results.append(result)
                except ValidationError:
                    continue
        
        return results
    
    def get_performance_trends(self, days: int = 30) -> Dict[str, List[float]]:
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        results = BenchmarkResult.objects.filter(
            created_at__gte=cutoff_date
        ).order_by('created_at')
        
        trends = {
            'scores': [],
            'complexity_scores': [],
            'security_scores': []
        }
        
        for result in results:
            trends['scores'].append(float(result.overall_score))
            trends['complexity_scores'].append(float(result.complexity_score))
            trends['security_scores'].append(float(result.security_score))
        
        return trends
    
    def _get_review_with_metrics(self, review_id: int) -> Optional[CodeReview]:
        try:
            return CodeReview.objects.select_related().prefetch_related(
                'reviewmetric_set'
            ).get(id=review_id, status='completed')
        except CodeReview.DoesNotExist:
            return None
    
    def _extract_metrics(self, review: CodeReview) -> Dict[str, Decimal]:
        metrics = {}
        
        for metric in review.reviewmetric_set.all():
            metrics[metric.metric_type] = metric.score
        
        return metrics
    
    def _calculate_weighted_score(self, metrics: Dict[str, Decimal]) -> Decimal:
        total_score = Decimal('0')
        
        for metric_type, weight in self.default_weights.items():
            if metric_type in metrics:
                total_score += metrics[metric_type] * weight
        
        return min(total_score, Decimal('100'))
    
    def _determine_grade(self, score: Decimal) -> str:
        if score >= Decimal('90'):
            return 'A'
        elif score >= Decimal('80'):
            return 'B'
        elif score >= Decimal('70'):
            return 'C'
        elif score >= Decimal('60'):
            return 'D'
        else:
            return 'F'
    
    def _save_benchmark_result(self, result: Dict[str, Any]) -> BenchmarkResult:
        return BenchmarkResult.objects.create(
            review_id=result['review_id'],
            overall_score=result['score'],
            grade=result['grade'],
            complexity_score=result['metrics'].get('complexity', Decimal('0')),
            security_score=result['metrics'].get('security', Decimal('0')),
            performance_score=result['metrics'].get('performance', Decimal('0'))
        )