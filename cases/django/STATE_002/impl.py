from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from typing import Optional, Dict, Any
from .models import Order, OrderItem, RefundTransaction
from .notifications import NotificationService
from .payment import PaymentService


class OrderCancellationService:
    """Service for handling order cancellations with business logic validation."""
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.payment_service = PaymentService()
    
    def cancel_order(self, order: Order, reason: str, user_id: int) -> Dict[str, Any]:
        """
        Cancel an order and process refund if applicable.
        
        Args:
            order: The order to cancel
            reason: Reason for cancellation
            user_id: ID of user requesting cancellation
            
        Returns:
            Dict containing cancellation details
        """
        with transaction.atomic():
            self._validate_cancellation_request(order, user_id)
            
            original_status = order.status
            refund_amount = self._calculate_refund_amount(order)
            
            order.status = 'cancelled'
            order.cancelled_at = timezone.now()
            order.cancellation_reason = reason
            order.cancelled_by_id = user_id
            order.save()
            
            refund_transaction = None
            if refund_amount > Decimal('0.00'):
                refund_transaction = self._process_refund(order, refund_amount)
            
            self._update_inventory(order)
            self._send_cancellation_notifications(order, original_status)
            
            return {
                'order_id': order.id,
                'status': 'cancelled',
                'refund_amount': refund_amount,
                'refund_transaction_id': refund_transaction.id if refund_transaction else None,
                'cancelled_at': order.cancelled_at
            }
    
    def _validate_cancellation_request(self, order: Order, user_id: int) -> None:
        """Validate that the cancellation request is valid."""
        if order.status == 'cancelled':
            raise ValidationError("Order is already cancelled")
        
        if order.customer_id != user_id and not self._is_admin_user(user_id):
            raise ValidationError("Unauthorized to cancel this order")
        
        if order.status == 'refunded':
            raise ValidationError("Cannot cancel an already refunded order")
    
    def _calculate_refund_amount(self, order: Order) -> Decimal:
        """Calculate the refund amount based on order status and items."""
        if order.status == 'pending':
            return order.total_amount
        elif order.status in ['processing', 'confirmed']:
            return order.total_amount - self._calculate_processing_fee(order)
        else:
            return Decimal('0.00')
    
    def _calculate_processing_fee(self, order: Order) -> Decimal:
        """Calculate processing fee for partially processed orders."""
        base_fee = Decimal('5.00')
        if order.total_amount > Decimal('100.00'):
            return base_fee + (order.total_amount * Decimal('0.02'))
        return base_fee
    
    def _process_refund(self, order: Order, amount: Decimal) -> RefundTransaction:
        """Process the refund transaction."""
        refund_result = self.payment_service.process_refund(
            order.payment_transaction_id,
            amount
        )
        
        return RefundTransaction.objects.create(
            order=order,
            amount=amount,
            transaction_id=refund_result['transaction_id'],
            status='completed',
            processed_at=timezone.now()
        )
    
    def _update_inventory(self, order: Order) -> None:
        """Restore inventory for cancelled order items."""
        for item in order.items.all():
            item.product.stock_quantity += item.quantity
            item.product.save()
    
    def _send_cancellation_notifications(self, order: Order, original_status: str) -> None:
        """Send notifications about order cancellation."""
        self.notification_service.send_order_cancelled_email(
            order.customer.email,
            order.id,
            original_status
        )
        
        if original_status in ['processing', 'confirmed']:
            self.notification_service.notify_fulfillment_team(
                f"Order {order.id} cancelled - halt processing"
            )
    
    def _is_admin_user(self, user_id: int) -> bool:
        """Check if user has admin privileges."""
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(id=user_id)
            return user.is_staff or user.is_superuser
        except User.DoesNotExist:
            return False