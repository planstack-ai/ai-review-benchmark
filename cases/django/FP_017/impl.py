from typing import List, Dict, Any, Optional
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime

from .models import CodeReview, ReviewMetric, ReviewResult


class CodeReviewBenchmarkService:
    
    def __init__(self):
        self.batch_size = 1000
        self.default_metrics = ['complexity', 'maintainability', 'security', 'performance']
    
    def bulk_create_reviews(self, review_data: List[Dict[str, Any]]) -> List[CodeReview]:
        validated_data = self._validate_review_data(review_data)
        review_objects = self._prepare_review_objects(validated_data)
        
        with transaction.atomic():
            created_reviews = CodeReview.objects.bulk_create(
                review_objects, 
                batch_size=self.batch_size,
                ignore_conflicts=False
            )
            self._create_associated_metrics(created_reviews, validated_data)
        
        return created_reviews
    
    def bulk_create_review_results(self, results_data: List[Dict[str, Any]]) -> List[ReviewResult]:
        validated_results = self._validate_results_data(results_data)
        result_objects = self._prepare_result_objects(validated_results)
        
        with transaction.atomic():
            return ReviewResult.objects.bulk_create(
                result_objects,
                batch_size=self.batch_size
            )
    
    def _validate_review_data(self, review_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        validated_data = []
        
        for data in review_data:
            if not data.get('repository_url') or not data.get('commit_hash'):
                raise ValidationError("Repository URL and commit hash are required")
            
            validated_item = {
                'repository_url': data['repository_url'],
                'commit_hash': data['commit_hash'],
                'language': data.get('language', 'python'),
                'created_at': data.get('created_at', timezone.now()),
                'status': data.get('status', 'pending'),
                'lines_of_code': data.get('lines_of_code', 0)
            }
            validated_data.append(validated_item)
        
        return validated_data
    
    def _prepare_review_objects(self, validated_data: List[Dict[str, Any]]) -> List[CodeReview]:
        review_objects = []
        
        for data in validated_data:
            review = CodeReview(
                repository_url=data['repository_url'],
                commit_hash=data['commit_hash'],
                language=data['language'],
                created_at=data['created_at'],
                status=data['status'],
                lines_of_code=data['lines_of_code']
            )
            review_objects.append(review)
        
        return review_objects
    
    def _create_associated_metrics(self, reviews: List[CodeReview], validated_data: List[Dict[str, Any]]) -> None:
        metric_objects = []
        
        for review, data in zip(reviews, validated_data):
            metrics = data.get('metrics', self.default_metrics)
            
            for metric_name in metrics:
                metric = ReviewMetric(
                    review=review,
                    metric_name=metric_name,
                    score=Decimal('0.0'),
                    weight=Decimal('1.0')
                )
                metric_objects.append(metric)
        
        if metric_objects:
            ReviewMetric.objects.bulk_create(metric_objects, batch_size=self.batch_size)
    
    def _validate_results_data(self, results_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        validated_results = []
        
        for data in results_data:
            if not data.get('review_id'):
                raise ValidationError("Review ID is required for results")
            
            validated_item = {
                'review_id': data['review_id'],
                'overall_score': min(max(data.get('overall_score', 0.0), 0.0), 100.0),
                'issues_found': data.get('issues_found', 0),
                'execution_time': data.get('execution_time', 0.0),
                'completed_at': data.get('completed_at', timezone.now())
            }
            validated_results.append(validated_item)
        
        return validated_results
    
    def _prepare_result_objects(self, validated_results: List[Dict[str, Any]]) -> List[ReviewResult]:
        result_objects = []
        
        for data in validated_results:
            result = ReviewResult(
                review_id=data['review_id'],
                overall_score=data['overall_score'],
                issues_found=data['issues_found'],
                execution_time=data['execution_time'],
                completed_at=data['completed_at']
            )
            result_objects.append(result)
        
        return result_objects