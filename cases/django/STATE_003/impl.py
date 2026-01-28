from decimal import Decimal
from typing import Optional, Dict, Any
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class PaymentProcessingService:
    """Service for handling payment processing operations."""
    
    def __init__(self):
        self.payment_gateway_timeout = getattr(settings, 'PAYMENT_GATEWAY_TIMEOUT', 30)
        self.max_retry_attempts = getattr(settings, 'PAYMENT_MAX_RETRIES', 3)
    
    def process_payment(self, order, payment_method: str, amount: Decimal) -> Dict[str, Any]:
        """Process payment for the given order."""
        if not self._validate_payment_amount(order, amount):
            raise ValidationError("Payment amount does not match order total")
        
        if not self._validate_payment_method(payment_method):
            raise ValidationError("Invalid payment method")
        
        payment_data = self._prepare_payment_data(order, payment_method, amount)
        
        with transaction.atomic():
            payment_result = self._execute_payment_transaction(payment_data)
            
            if payment_result['status'] == 'success':
                self._update_order_status(order, 'paid')
                self._send_payment_confirmation(order, payment_result)
                logger.info(f"Payment processed successfully for order {order.id}")
                
            return payment_result
    
    def _validate_payment_amount(self, order, amount: Decimal) -> bool:
        """Validate that payment amount matches order total."""
        return abs(order.total_amount - amount) < Decimal('0.01')
    
    def _validate_payment_method(self, payment_method: str) -> bool:
        """Validate the payment method is supported."""
        supported_methods = ['credit_card', 'debit_card', 'paypal', 'bank_transfer']
        return payment_method in supported_methods
    
    def _prepare_payment_data(self, order, payment_method: str, amount: Decimal) -> Dict[str, Any]:
        """Prepare payment data for gateway submission."""
        return {
            'order_id': order.id,
            'amount': str(amount),
            'currency': order.currency,
            'payment_method': payment_method,
            'customer_id': order.customer.id,
            'timestamp': timezone.now().isoformat(),
            'merchant_reference': f"ORDER-{order.id}-{timezone.now().strftime('%Y%m%d')}"
        }
    
    def _execute_payment_transaction(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual payment transaction with the gateway."""
        try:
            gateway_response = self._call_payment_gateway(payment_data)
            
            if gateway_response.get('transaction_id'):
                return {
                    'status': 'success',
                    'transaction_id': gateway_response['transaction_id'],
                    'gateway_response': gateway_response,
                    'processed_at': timezone.now()
                }
            else:
                return {
                    'status': 'failed',
                    'error_code': gateway_response.get('error_code', 'UNKNOWN'),
                    'error_message': gateway_response.get('error_message', 'Payment failed'),
                    'processed_at': timezone.now()
                }
                
        except Exception as e:
            logger.error(f"Payment gateway error: {str(e)}")
            return {
                'status': 'error',
                'error_message': 'Payment processing temporarily unavailable',
                'processed_at': timezone.now()
            }
    
    def _call_payment_gateway(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate payment gateway call."""
        import uuid
        import random
        
        if random.random() > 0.1:
            return {
                'transaction_id': str(uuid.uuid4()),
                'status': 'approved',
                'authorization_code': f"AUTH{random.randint(100000, 999999)}"
            }
        else:
            return {
                'error_code': 'DECLINED',
                'error_message': 'Payment declined by issuer'
            }
    
    def _update_order_status(self, order, status: str) -> None:
        """Update order status after successful payment."""
        order.status = status
        order.paid_at = timezone.now()
        order.save(update_fields=['status', 'paid_at'])
    
    def _send_payment_confirmation(self, order, payment_result: Dict[str, Any]) -> None:
        """Send payment confirmation to customer."""
        logger.info(f"Sending payment confirmation for order {order.id}")