from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from django.db import transaction
from django.db.models import QuerySet, F, Sum, Count, Avg
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta

from .models import CodeReview, ReviewMetric, Benchmark, ReviewerProfile


class CodeReviewBenchmarkService:
    
    def __init__(self):
        self.cache_timeout = 3600
        self.batch_size = 1000
    
    def calculate_reviewer_performance_metrics(self, reviewer_id: int, 
                                             start_date: datetime, 
                                             end_date: datetime) -> Dict[str, Decimal]:
        cache_key = f"reviewer_metrics_{reviewer_id}_{start_date.date()}_{end_date.date()}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        reviews = self._get_reviewer_reviews(reviewer_id, start_date, end_date)
        
        metrics = {
            'total_reviews': Decimal(str(reviews.count())),
            'avg_review_time': self._calculate_avg_review_time(reviews),
            'accuracy_score': self._calculate_accuracy_score(reviews),
            'throughput_score': self._calculate_throughput_score(reviews),
            'quality_score': self._calculate_quality_score(reviews)
        }
        
        overall_score = self._compute_overall_benchmark_score(metrics)
        metrics['overall_benchmark_score'] = overall_score
        
        cache.set(cache_key, metrics, self.cache_timeout)
        return metrics
    
    def update_denormalized_benchmark_data(self, benchmark_id: int) -> bool:
        try:
            with transaction.atomic():
                benchmark = Benchmark.objects.select_for_update().get(id=benchmark_id)
                
                aggregated_data = self._aggregate_benchmark_metrics(benchmark_id)
                
                benchmark.total_reviews_count = aggregated_data['total_reviews']
                benchmark.avg_accuracy_score = aggregated_data['avg_accuracy']
                benchmark.avg_review_time_minutes = aggregated_data['avg_time']
                benchmark.top_performer_score = aggregated_data['top_score']
                benchmark.last_updated = timezone.now()
                
                benchmark.save(update_fields=[
                    'total_reviews_count', 'avg_accuracy_score', 
                    'avg_review_time_minutes', 'top_performer_score', 'last_updated'
                ])
                
                self._invalidate_related_caches(benchmark_id)
                return True
                
        except Benchmark.DoesNotExist:
            return False
    
    def get_benchmark_leaderboard(self, benchmark_id: int, limit: int = 10) -> List[Dict]:
        cache_key = f"leaderboard_{benchmark_id}_{limit}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        top_reviewers = ReviewerProfile.objects.filter(
            reviews__benchmark_id=benchmark_id
        ).annotate(
            review_count=Count('reviews'),
            avg_score=Avg('reviews__overall_score'),
            avg_time=Avg('reviews__review_time_minutes')
        ).filter(
            review_count__gte=5
        ).order_by('-avg_score', 'avg_time')[:limit]
        
        leaderboard = []
        for idx, reviewer in enumerate(top_reviewers, 1):
            leaderboard.append({
                'rank': idx,
                'reviewer_id': reviewer.id,
                'username': reviewer.username,
                'review_count': reviewer.review_count,
                'avg_score': reviewer.avg_score,
                'avg_time_minutes': reviewer.avg_time
            })
        
        cache.set(cache_key, leaderboard, self.cache_timeout)
        return leaderboard
    
    def _get_reviewer_reviews(self, reviewer_id: int, start_date: datetime, 
                            end_date: datetime) -> QuerySet:
        return CodeReview.objects.filter(
            reviewer_id=reviewer_id,
            created_at__range=(start_date, end_date),
            status='completed'
        ).select_related('benchmark')
    
    def _calculate_avg_review_time(self, reviews: QuerySet) -> Decimal:
        avg_time = reviews.aggregate(avg_time=Avg('review_time_minutes'))['avg_time']
        return Decimal(str(avg_time or 0))
    
    def _calculate_accuracy_score(self, reviews: QuerySet) -> Decimal:
        total_accuracy = reviews.aggregate(total=Sum('accuracy_score'))['total']
        count = reviews.count()
        return Decimal(str(total_accuracy / count if count > 0 else 0))
    
    def _calculate_throughput_score(self, reviews: QuerySet) -> Decimal:
        count = reviews.count()
        days_span = 7
        return Decimal(str(count / days_span))
    
    def _calculate_quality_score(self, reviews: QuerySet) -> Decimal:
        quality_sum = reviews.aggregate(total=Sum('quality_rating'))['total']
        count = reviews.count()
        return Decimal(str(quality_sum / count if count > 0 else 0))
    
    def _compute_overall_benchmark_score(self, metrics: Dict[str, Decimal]) -> Decimal:
        weights = {
            'accuracy_score': Decimal('0.4'),
            'quality_score': Decimal('0.3'),
            'throughput_score': Decimal('0.2'),
            'avg_review_time': Decimal('0.1')
        }
        
        normalized_time = max(Decimal('1'), Decimal('60') - metrics['avg_review_time'])
        
        score = (
            metrics['accuracy_score'] * weights['accuracy_score'] +
            metrics['quality_score'] * weights['quality_score'] +
            metrics['throughput_score'] * weights['throughput_score'] +
            normalized_time * weights['avg_review_time']
        )
        
        return min(score, Decimal('100'))
    
    def _aggregate_benchmark_metrics(self, benchmark_id: int) -> Dict:
        reviews = CodeReview.objects.filter(benchmark_id=benchmark_id, status='completed')
        
        return {
            'total_reviews': reviews.count(),
            'avg_accuracy': reviews.aggregate(avg=Avg('accuracy_score'))['avg'] or 0,
            'avg_time': reviews.aggregate(avg=Avg('review_time_minutes'))['avg'] or 0,
            'top_score': reviews.aggregate(max_score=Avg('overall_score'))['max_score'] or 0
        }
    
    def _invalidate_related_caches(self, benchmark_id: int) -> None:
        cache_patterns = [
            f"leaderboard_{benchmark_id}_*",
            f"benchmark_stats_{benchmark_id}",
            f"reviewer_metrics_*"
        ]
        
        for pattern in cache_patterns:
            cache.delete_many(cache.keys(pattern))