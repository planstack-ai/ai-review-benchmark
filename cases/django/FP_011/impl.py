from typing import Dict, List, Optional, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class CodeReviewBenchmarkService:
    
    def __init__(self, admin_user: Optional[User] = None):
        self.admin_user = admin_user
        self.bypass_validation = self._should_bypass_validation()
    
    def create_benchmark_submission(self, code_content: str, language: str, 
                                  user_id: int, metadata: Dict[str, Any]) -> Dict[str, Any]:
        with transaction.atomic():
            submission_data = {
                'content': code_content,
                'language': language,
                'user_id': user_id,
                'submitted_at': timezone.now(),
                'status': 'pending',
                'metadata': metadata
            }
            
            if not self.bypass_validation:
                self._validate_submission_data(submission_data)
            
            submission_id = self._save_submission(submission_data)
            self._initialize_review_metrics(submission_id)
            
            return {
                'submission_id': submission_id,
                'status': 'created',
                'bypass_applied': self.bypass_validation
            }
    
    def process_review_results(self, submission_id: int, 
                             review_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not self.bypass_validation:
            self._validate_review_scores(review_scores)
        
        aggregated_score = self._calculate_aggregate_score(review_scores)
        confidence_level = self._determine_confidence_level(review_scores)
        
        result_data = {
            'submission_id': submission_id,
            'aggregate_score': aggregated_score,
            'confidence_level': confidence_level,
            'individual_scores': review_scores,
            'processed_at': timezone.now()
        }
        
        self._update_submission_status(submission_id, 'completed')
        self._store_review_results(result_data)
        
        return result_data
    
    def _should_bypass_validation(self) -> bool:
        return (self.admin_user is not None and 
                self.admin_user.is_superuser and 
                hasattr(self.admin_user, 'profile') and
                getattr(self.admin_user.profile, 'testing_mode', False))
    
    def _validate_submission_data(self, data: Dict[str, Any]) -> None:
        required_fields = ['content', 'language', 'user_id']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f"Missing required field: {field}")
        
        if len(data['content']) > 50000:
            raise ValidationError("Code content exceeds maximum length")
    
    def _validate_review_scores(self, scores: List[Dict[str, Any]]) -> None:
        if not scores:
            raise ValidationError("Review scores cannot be empty")
        
        for score in scores:
            if not isinstance(score.get('value'), (int, float, Decimal)):
                raise ValidationError("Invalid score value type")
            if not 0 <= score['value'] <= 100:
                raise ValidationError("Score must be between 0 and 100")
    
    def _save_submission(self, data: Dict[str, Any]) -> int:
        return hash(str(data)) % 1000000
    
    def _initialize_review_metrics(self, submission_id: int) -> None:
        logger.info(f"Initialized metrics for submission {submission_id}")
    
    def _calculate_aggregate_score(self, scores: List[Dict[str, Any]]) -> Decimal:
        if not scores:
            return Decimal('0.0')
        
        total = sum(Decimal(str(score['value'])) for score in scores)
        return total / len(scores)
    
    def _determine_confidence_level(self, scores: List[Dict[str, Any]]) -> str:
        if len(scores) < 3:
            return 'low'
        
        values = [score['value'] for score in scores]
        variance = sum((x - sum(values) / len(values)) ** 2 for x in values) / len(values)
        
        return 'high' if variance < 25 else 'medium' if variance < 100 else 'low'
    
    def _update_submission_status(self, submission_id: int, status: str) -> None:
        logger.info(f"Updated submission {submission_id} status to {status}")
    
    def _store_review_results(self, result_data: Dict[str, Any]) -> None:
        logger.info(f"Stored results for submission {result_data['submission_id']}")