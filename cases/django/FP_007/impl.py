from typing import Dict, List, Optional, Any
from django.db import transaction
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class CodeReviewBenchmarkService:
    
    def __init__(self):
        self.signal_chain: List[str] = []
        self.callback_registry: Dict[str, Any] = {}
        self.processing_state = {
            'validation_complete': False,
            'metrics_calculated': False,
            'notifications_sent': False
        }
    
    def process_benchmark_submission(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        self.signal_chain.clear()
        self._reset_processing_state()
        
        try:
            with transaction.atomic():
                validated_data = self._validate_submission(submission_data)
                benchmark_result = self._calculate_metrics(validated_data)
                self._trigger_notification_chain(benchmark_result)
                
                return {
                    'success': True,
                    'benchmark_id': benchmark_result.get('id'),
                    'signal_chain': self.signal_chain.copy(),
                    'processing_state': self.processing_state.copy()
                }
        except ValidationError as e:
            logger.error(f"Validation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _validate_submission(self, data: Dict[str, Any]) -> Dict[str, Any]:
        required_fields = ['code_content', 'language', 'complexity_score']
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        if not isinstance(data['complexity_score'], (int, float, Decimal)):
            raise ValidationError("Complexity score must be numeric")
        
        self._register_callback('validation_complete', self._on_validation_complete)
        self._trigger_callback('validation_complete', data)
        
        return data
    
    def _calculate_metrics(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        complexity_score = Decimal(str(validated_data['complexity_score']))
        code_length = len(validated_data['code_content'])
        
        metrics = {
            'id': f"benchmark_{timezone.now().timestamp()}",
            'complexity_score': complexity_score,
            'code_length': code_length,
            'readability_score': self._calculate_readability_score(code_length, complexity_score),
            'timestamp': timezone.now()
        }
        
        self._register_callback('metrics_calculated', self._on_metrics_calculated)
        self._trigger_callback('metrics_calculated', metrics)
        
        return metrics
    
    def _calculate_readability_score(self, code_length: int, complexity: Decimal) -> Decimal:
        base_score = Decimal('100.0')
        length_penalty = Decimal(str(code_length)) / Decimal('1000.0')
        complexity_penalty = complexity * Decimal('2.0')
        
        return max(Decimal('0.0'), base_score - length_penalty - complexity_penalty)
    
    def _trigger_notification_chain(self, benchmark_result: Dict[str, Any]) -> None:
        notification_types = ['email', 'webhook', 'dashboard']
        
        for notification_type in notification_types:
            callback_name = f"notify_{notification_type}"
            self._register_callback(callback_name, getattr(self, f"_send_{notification_type}_notification"))
            self._trigger_callback(callback_name, benchmark_result)
        
        self._register_callback('notifications_complete', self._on_notifications_complete)
        self._trigger_callback('notifications_complete', benchmark_result)
    
    def _register_callback(self, event_name: str, callback_func) -> None:
        self.callback_registry[event_name] = callback_func
    
    def _trigger_callback(self, event_name: str, data: Any) -> None:
        if event_name in self.callback_registry:
            self.signal_chain.append(event_name)
            self.callback_registry[event_name](data)
    
    def _on_validation_complete(self, data: Dict[str, Any]) -> None:
        self.processing_state['validation_complete'] = True
        logger.info(f"Validation completed for submission with {len(data)} fields")
    
    def _on_metrics_calculated(self, metrics: Dict[str, Any]) -> None:
        self.processing_state['metrics_calculated'] = True
        logger.info(f"Metrics calculated for benchmark {metrics['id']}")
    
    def _send_email_notification(self, result: Dict[str, Any]) -> None:
        logger.info(f"Email notification sent for benchmark {result['id']}")
    
    def _send_webhook_notification(self, result: Dict[str, Any]) -> None:
        logger.info(f"Webhook notification sent for benchmark {result['id']}")
    
    def _send_dashboard_notification(self, result: Dict[str, Any]) -> None:
        logger.info(f"Dashboard notification sent for benchmark {result['id']}")
    
    def _on_notifications_complete(self, result: Dict[str, Any]) -> None:
        self.processing_state['notifications_sent'] = True
        logger.info(f"All notifications completed for benchmark {result['id']}")
    
    def _reset_processing_state(self) -> None:
        for key in self.processing_state:
            self.processing_state[key] = False