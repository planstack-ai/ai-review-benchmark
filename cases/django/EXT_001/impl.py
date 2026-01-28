from decimal import Decimal
from typing import Optional, Dict, Any
import requests
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging

from .models import Order, Payment, PaymentStatus
from .exceptions import PaymentProcessingError, InsufficientFundsError

logger = logging.getLogger(__name__)


class PaymentService:
    
    def __init__(self):
        self.api_base_url = settings.PAYMENT_API_BASE_URL
        self.api_key = settings.PAYMENT_API_KEY
        self.timeout = getattr(settings, 'PAYMENT_API_TIMEOUT', 30)
    
    def process_payment(self, order_id: int, payment_method: str, amount: Decimal) -> Payment:
        order = self._get_order(order_id)
        self._validate_payment_amount(order, amount)
        
        with transaction.atomic():
            payment = self._create_payment_record(order, payment_method, amount)
            
            try:
                response = self._call_payment_api(payment)
                return self._handle_payment_response(payment, response)
            except requests.ConnectionError as e:
                logger.error(f"Payment API connection failed for payment {payment.id}: {e}")
                payment.status = PaymentStatus.FAILED
                payment.error_message = "Connection to payment provider failed"
                payment.save()
                raise PaymentProcessingError("Unable to connect to payment provider")
            except requests.Timeout:
                logger.error(f"Payment API timeout for payment {payment.id}")
                raise PaymentProcessingError("Payment request timed out")
            except requests.RequestException as e:
                logger.error(f"Payment API error for payment {payment.id}: {e}")
                payment.status = PaymentStatus.FAILED
                payment.error_message = str(e)
                payment.save()
                raise PaymentProcessingError("Payment processing failed")
    
    def _get_order(self, order_id: int) -> Order:
        try:
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise ValidationError(f"Order {order_id} not found")
    
    def _validate_payment_amount(self, order: Order, amount: Decimal) -> None:
        if amount != order.total_amount:
            raise ValidationError("Payment amount does not match order total")
        
        if amount <= Decimal('0'):
            raise ValidationError("Payment amount must be positive")
    
    def _create_payment_record(self, order: Order, payment_method: str, amount: Decimal) -> Payment:
        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=amount,
            status=PaymentStatus.PROCESSING,
            created_at=timezone.now()
        )
        
        order.status = 'payment_processing'
        order.save()
        
        return payment
    
    def _call_payment_api(self, payment: Payment) -> Dict[str, Any]:
        payload = {
            'payment_id': payment.id,
            'amount': str(payment.amount),
            'currency': 'USD',
            'payment_method': payment.payment_method,
            'order_reference': payment.order.reference_number
        }
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{self.api_base_url}/payments",
            json=payload,
            headers=headers,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        return response.json()
    
    def _handle_payment_response(self, payment: Payment, response_data: Dict[str, Any]) -> Payment:
        status = response_data.get('status')
        transaction_id = response_data.get('transaction_id')
        
        if status == 'approved':
            payment.status = PaymentStatus.COMPLETED
            payment.transaction_id = transaction_id
            payment.completed_at = timezone.now()
            payment.order.status = 'paid'
            payment.order.save()
        elif status == 'declined':
            payment.status = PaymentStatus.FAILED
            payment.error_message = response_data.get('decline_reason', 'Payment declined')
            raise InsufficientFundsError("Payment was declined by the provider")
        else:
            payment.status = PaymentStatus.PENDING
            payment.transaction_id = transaction_id
        
        payment.save()
        return payment