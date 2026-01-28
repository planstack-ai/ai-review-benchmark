from typing import List, Dict, Any, Optional
from decimal import Decimal
from django.db import transaction
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime

from .models import CodeReview, ReviewMetric, BenchmarkResult


class CodeReviewBenchmarkService:
    
    def __init__(self):
        self.batch_size = 1000
        self.performance_threshold = Decimal('0.85')
    
    def bulk_update_review_scores(self, review_ids: List[int], score_data: Dict[int, Dict[str, Any]]) -> int:
        if not review_ids or not score_data:
            raise ValidationError("Review IDs and score data cannot be empty")
        
        reviews = self._fetch_reviews_for_update(review_ids)
        updated_reviews = self._prepare_review_updates(reviews, score_data)
        
        return self._execute_bulk_update(updated_reviews)
    
    def bulk_update_benchmark_results(self, results_data: List[Dict[str, Any]]) -> int:
        if not results_data:
            return 0
        
        validated_data = self._validate_benchmark_data(results_data)
        processed_batches = self._split_into_batches(validated_data)
        
        total_updated = 0
        for batch in processed_batches:
            total_updated += self._process_benchmark_batch(batch)
        
        return total_updated
    
    def update_performance_metrics(self, metric_updates: Dict[str, Decimal]) -> bool:
        if not metric_updates:
            return False
        
        metric_objects = self._build_metric_objects(metric_updates)
        
        with transaction.atomic():
            updated_count = ReviewMetric.objects.bulk_update(
                metric_objects,
                ['accuracy_score', 'precision_score', 'recall_score', 'updated_at'],
                batch_size=self.batch_size
            )
        
        return updated_count > 0
    
    def _fetch_reviews_for_update(self, review_ids: List[int]) -> QuerySet:
        return CodeReview.objects.filter(
            id__in=review_ids,
            status__in=['pending', 'in_progress']
        ).select_for_update()
    
    def _prepare_review_updates(self, reviews: QuerySet, score_data: Dict[int, Dict[str, Any]]) -> List[CodeReview]:
        updated_reviews = []
        current_time = timezone.now()
        
        for review in reviews:
            if review.id in score_data:
                data = score_data[review.id]
                review.overall_score = Decimal(str(data.get('score', 0)))
                review.complexity_rating = data.get('complexity', 1)
                review.quality_rating = data.get('quality', 1)
                review.updated_at = current_time
                
                if review.overall_score >= self.performance_threshold:
                    review.status = 'approved'
                
                updated_reviews.append(review)
        
        return updated_reviews
    
    def _execute_bulk_update(self, reviews: List[CodeReview]) -> int:
        if not reviews:
            return 0
        
        with transaction.atomic():
            return CodeReview.objects.bulk_update(
                reviews,
                ['overall_score', 'complexity_rating', 'quality_rating', 'status', 'updated_at'],
                batch_size=self.batch_size
            )
    
    def _validate_benchmark_data(self, results_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        validated_data = []
        
        for data in results_data:
            if self._is_valid_benchmark_entry(data):
                validated_data.append(data)
        
        return validated_data
    
    def _is_valid_benchmark_entry(self, data: Dict[str, Any]) -> bool:
        required_fields = ['benchmark_id', 'execution_time', 'memory_usage']
        return all(field in data for field in required_fields)
    
    def _split_into_batches(self, data: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        batches = []
        for i in range(0, len(data), self.batch_size):
            batches.append(data[i:i + self.batch_size])
        return batches
    
    def _process_benchmark_batch(self, batch: List[Dict[str, Any]]) -> int:
        benchmark_objects = []
        
        for data in batch:
            benchmark = BenchmarkResult(
                benchmark_id=data['benchmark_id'],
                execution_time=Decimal(str(data['execution_time'])),
                memory_usage=data['memory_usage'],
                updated_at=timezone.now()
            )
            benchmark_objects.append(benchmark)
        
        with transaction.atomic():
            return BenchmarkResult.objects.bulk_update(
                benchmark_objects,
                ['execution_time', 'memory_usage', 'updated_at'],
                batch_size=len(benchmark_objects)
            )
    
    def _build_metric_objects(self, metric_updates: Dict[str, Decimal]) -> List[ReviewMetric]:
        metric_names = list(metric_updates.keys())
        existing_metrics = ReviewMetric.objects.filter(metric_name__in=metric_names)
        
        for metric in existing_metrics:
            if metric.metric_name in metric_updates:
                metric.accuracy_score = metric_updates[metric.metric_name]
                metric.precision_score = metric_updates.get(f"{metric.metric_name}_precision", Decimal('0'))
                metric.recall_score = metric_updates.get(f"{metric.metric_name}_recall", Decimal('0'))
                metric.updated_at = timezone.now()
        
        return list(existing_metrics)