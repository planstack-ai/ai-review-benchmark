from decimal import Decimal
from typing import Optional, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from orders.models import Order, Payment
from payments.exceptions import PaymentProcessingError, InsufficientFundsError


class PaymentProcessingService:
    """Service for handling payment processing operations."""
    
    def __init__(self):
        self.payment_gateway = self._get_payment_gateway()
    
    def process_payment(self, order_id: int, payment_method: str, amount: Decimal) -> Dict[str, Any]:
        """Process payment for the given order."""
        try:
            order = Order.objects.get(id=order_id)
            self._validate_payment_request(order, amount)
            
            with transaction.atomic():
                payment_result = self._execute_payment_transaction(
                    order, payment_method, amount
                )
                
                if payment_result['success']:
                    self._finalize_successful_payment(order, payment_result)
                    return {
                        'success': True,
                        'transaction_id': payment_result['transaction_id'],
                        'amount_charged': amount,
                        'order_id': order_id
                    }
                else:
                    return {
                        'success': False,
                        'error': payment_result.get('error', 'Payment failed'),
                        'order_id': order_id
                    }
                    
        except Order.DoesNotExist:
            raise ValidationError(f"Order {order_id} not found")
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'order_id': order_id
            }
    
    def _validate_payment_request(self, order: Order, amount: Decimal) -> None:
        """Validate the payment request parameters."""
        if order.status == 'cancelled':
            raise ValidationError("Cannot process payment for cancelled order")
        
        if amount <= 0:
            raise ValidationError("Payment amount must be positive")
        
        if amount != order.total_amount:
            raise ValidationError("Payment amount does not match order total")
    
    def _execute_payment_transaction(self, order: Order, payment_method: str, amount: Decimal) -> Dict[str, Any]:
        """Execute the actual payment transaction with the gateway."""
        try:
            gateway_response = self.payment_gateway.charge(
                amount=amount,
                payment_method=payment_method,
                order_reference=str(order.id)
            )
            
            return {
                'success': gateway_response.get('status') == 'completed',
                'transaction_id': gateway_response.get('transaction_id'),
                'gateway_response': gateway_response,
                'error': gateway_response.get('error_message')
            }
            
        except InsufficientFundsError:
            return {'success': False, 'error': 'Insufficient funds'}
        except PaymentProcessingError as e:
            return {'success': False, 'error': str(e)}
    
    def _finalize_successful_payment(self, order: Order, payment_result: Dict[str, Any]) -> None:
        """Finalize the order after successful payment."""
        Payment.objects.create(
            order=order,
            amount=order.total_amount,
            transaction_id=payment_result['transaction_id'],
            payment_method=payment_result['gateway_response'].get('payment_method'),
            processed_at=timezone.now(),
            status='completed'
        )
        
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save()
    
    def _get_payment_gateway(self):
        """Get the configured payment gateway instance."""
        from payments.gateways import get_default_gateway
        return get_default_gateway()