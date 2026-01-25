from decimal import Decimal
from typing import Optional, Dict, Any, List
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from datetime import datetime

from .models import CodeReview, ReviewMetric, BenchmarkResult


class CodeReviewBenchmarkService:
    
    def __init__(self):
        self.min_score_threshold = Decimal('0.0')
        self.max_score_threshold = Decimal('100.0')
        self.required_metrics = ['complexity', 'maintainability', 'security']
    
    def create_benchmark_review(self, code_snippet: str, language: str, 
                              reviewer_id: int) -> CodeReview:
        self._validate_code_snippet(code_snippet)
        self._validate_language(language)
        
        with transaction.atomic():
            review = CodeReview.objects.create(
                code_snippet=code_snippet,
                language=language,
                reviewer_id=reviewer_id,
                status='pending',
                created_at=timezone.now()
            )
            
            self._initialize_default_metrics(review)
            return review
    
    def calculate_overall_score(self, review_id: int) -> Decimal:
        review = self._get_review_by_id(review_id)
        metrics = ReviewMetric.objects.filter(review=review)
        
        if not metrics.exists():
            raise ValidationError("No metrics found for review")
        
        total_weight = Decimal('0.0')
        weighted_score = Decimal('0.0')
        
        for metric in metrics:
            self._validate_metric_score(metric.score)
            weighted_score += metric.score * metric.weight
            total_weight += metric.weight
        
        if total_weight == 0:
            return Decimal('0.0')
        
        overall_score = weighted_score / total_weight
        review.overall_score = overall_score
        review.save(update_fields=['overall_score'])
        
        return overall_score
    
    def generate_benchmark_result(self, review_id: int, 
                                expected_score: Decimal) -> BenchmarkResult:
        review = self._get_review_by_id(review_id)
        actual_score = self.calculate_overall_score(review_id)
        
        accuracy = self._calculate_accuracy(actual_score, expected_score)
        
        result = BenchmarkResult.objects.create(
            review=review,
            expected_score=expected_score,
            actual_score=actual_score,
            accuracy=accuracy,
            is_passed=accuracy >= Decimal('0.8'),
            generated_at=timezone.now()
        )
        
        return result
    
    def _validate_code_snippet(self, code_snippet: str) -> None:
        if not code_snippet or not code_snippet.strip():
            raise ValidationError("Code snippet cannot be empty")
        
        if len(code_snippet) > 10000:
            raise ValidationError("Code snippet too long")
    
    def _validate_language(self, language: str) -> None:
        supported_languages = ['python', 'javascript', 'java', 'cpp', 'go']
        if language.lower() not in supported_languages:
            raise ValidationError(f"Unsupported language: {language}")
    
    def _validate_metric_score(self, score: Decimal) -> None:
        if score < self.min_score_threshold or score > self.max_score_threshold:
            raise ValidationError(
                f"Score must be between {self.min_score_threshold} and {self.max_score_threshold}"
            )
    
    def _get_review_by_id(self, review_id: int) -> CodeReview:
        try:
            return CodeReview.objects.get(id=review_id)
        except CodeReview.DoesNotExist:
            raise ValidationError(f"Review with id {review_id} not found")
    
    def _initialize_default_metrics(self, review: CodeReview) -> None:
        default_metrics = [
            {'name': 'complexity', 'weight': Decimal('0.3')},
            {'name': 'maintainability', 'weight': Decimal('0.4')},
            {'name': 'security', 'weight': Decimal('0.3')}
        ]
        
        for metric_data in default_metrics:
            ReviewMetric.objects.create(
                review=review,
                metric_name=metric_data['name'],
                score=Decimal('0.0'),
                weight=metric_data['weight']
            )
    
    def _calculate_accuracy(self, actual: Decimal, expected: Decimal) -> Decimal:
        if expected == 0:
            return Decimal('1.0') if actual == 0 else Decimal('0.0')
        
        difference = abs(actual - expected)
        accuracy = max(Decimal('0.0'), Decimal('1.0') - (difference / expected))
        return accuracy