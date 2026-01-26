from typing import List, Dict, Any, Optional
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from asgiref.sync import sync_to_async
import asyncio
import logging

from .models import CodeReview, ReviewMetric, BenchmarkResult
from .serializers import CodeReviewSerializer

logger = logging.getLogger(__name__)


class AsyncCodeReviewBenchmarkService:
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.pending_reviews: List[Dict[str, Any]] = []
        self.pending_metrics: List[Dict[str, Any]] = []
    
    async def process_code_review_batch(self, review_data: List[Dict[str, Any]]) -> List[int]:
        validated_data = await self._validate_review_batch(review_data)
        review_ids = await self._bulk_create_reviews(validated_data)
        await self._update_benchmark_statistics(len(review_ids))
        return review_ids
    
    async def queue_review_for_processing(self, review_data: Dict[str, Any]) -> None:
        self.pending_reviews.append(review_data)
        
        if len(self.pending_reviews) >= self.batch_size:
            await self._flush_pending_reviews()
    
    async def queue_metric_data(self, metric_data: Dict[str, Any]) -> None:
        enriched_metric = await self._enrich_metric_data(metric_data)
        self.pending_metrics.append(enriched_metric)
        
        if len(self.pending_metrics) >= self.batch_size:
            await self._flush_pending_metrics()
    
    async def force_flush_all(self) -> Dict[str, int]:
        review_count = await self._flush_pending_reviews()
        metric_count = await self._flush_pending_metrics()
        
        return {
            'reviews_processed': review_count,
            'metrics_processed': metric_count
        }
    
    async def _validate_review_batch(self, review_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        validated_reviews = []
        
        for data in review_data:
            serializer = CodeReviewSerializer(data=data)
            if await sync_to_async(serializer.is_valid)():
                validated_reviews.append(serializer.validated_data)
            else:
                logger.warning(f"Invalid review data: {serializer.errors}")
        
        return validated_reviews
    
    async def _bulk_create_reviews(self, validated_data: List[Dict[str, Any]]) -> List[int]:
        review_objects = [
            CodeReview(**data) for data in validated_data
        ]
        
        created_reviews = await sync_to_async(CodeReview.objects.bulk_create)(
            review_objects, batch_size=self.batch_size
        )
        
        return [review.id for review in created_reviews]
    
    async def _flush_pending_reviews(self) -> int:
        if not self.pending_reviews:
            return 0
        
        count = len(self.pending_reviews)
        await self.process_code_review_batch(self.pending_reviews)
        self.pending_reviews.clear()
        return count
    
    async def _flush_pending_metrics(self) -> int:
        if not self.pending_metrics:
            return 0
        
        count = len(self.pending_metrics)
        metric_objects = [ReviewMetric(**data) for data in self.pending_metrics]
        
        await sync_to_async(ReviewMetric.objects.bulk_create)(
            metric_objects, batch_size=self.batch_size
        )
        
        self.pending_metrics.clear()
        return count
    
    async def _enrich_metric_data(self, metric_data: Dict[str, Any]) -> Dict[str, Any]:
        enriched = metric_data.copy()
        enriched['timestamp'] = timezone.now()
        enriched['processing_time'] = await self._calculate_processing_time(metric_data)
        return enriched
    
    async def _calculate_processing_time(self, metric_data: Dict[str, Any]) -> Decimal:
        complexity_factor = metric_data.get('complexity_score', 1.0)
        base_time = Decimal('0.5')
        return base_time * Decimal(str(complexity_factor))
    
    async def _update_benchmark_statistics(self, processed_count: int) -> None:
        await sync_to_async(BenchmarkResult.objects.filter(
            is_active=True
        ).update)(
            total_processed=models.F('total_processed') + processed_count,
            last_updated=timezone.now()
        )