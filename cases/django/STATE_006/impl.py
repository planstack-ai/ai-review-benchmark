from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from typing import Optional, Dict, Any
import logging

from .models import Order, Payment, RefundTransaction
from .exceptions import RefundProcessingError, InsufficientFundsError

logger = logging.getLogger(__name__)


class RefundService:
    """Service class for handling payment refunds and related operations."""
    
    def __init__(self):
        self.payment_gateway = self._get_payment_gateway()
    
    def process_refund(self, order_id: int, refund_amount: Optional[Decimal] = None, 
                      reason: str = "Customer request") -> RefundTransaction:
        """
        Process a refund for the given order.
        
        Args:
            order_id: The ID of the order to refund
            refund_amount: Amount to refund (defaults to full order amount)
            reason: Reason for the refund
            
        Returns:
            RefundTransaction: The created refund transaction
            
        Raises:
            RefundProcessingError: If refund processing fails
            ValidationError: If validation fails
        """
        try:
            with transaction.atomic():
                order = self._get_order(order_id)
                self._validate_refund_eligibility(order)
                
                refund_amount = refund_amount or order.total_amount
                self._validate_refund_amount(order, refund_amount)
                
                refund_transaction = self._create_refund_transaction(
                    order, refund_amount, reason
                )
                
                gateway_response = self._process_gateway_refund(
                    order.payment, refund_amount
                )
                
                self._update_refund_transaction(refund_transaction, gateway_response)
                self._update_order_totals(order, refund_amount)
                
                logger.info(f"Refund processed successfully for order {order_id}")
                return refund_transaction
                
        except Exception as e:
            logger.error(f"Refund processing failed for order {order_id}: {str(e)}")
            raise RefundProcessingError(f"Failed to process refund: {str(e)}")
    
    def _get_order(self, order_id: int) -> Order:
        """Retrieve order by ID with related payment information."""
        try:
            return Order.objects.select_related('payment').get(id=order_id)
        except Order.DoesNotExist:
            raise ValidationError(f"Order with ID {order_id} not found")
    
    def _validate_refund_eligibility(self, order: Order) -> None:
        """Validate that the order is eligible for refund."""
        if not order.payment:
            raise ValidationError("Order has no associated payment")
        
        if order.payment.status != 'completed':
            raise ValidationError("Cannot refund incomplete payment")
        
        if order.status == 'cancelled':
            raise ValidationError("Cannot refund cancelled order")
    
    def _validate_refund_amount(self, order: Order, refund_amount: Decimal) -> None:
        """Validate the refund amount against order totals."""
        if refund_amount <= 0:
            raise ValidationError("Refund amount must be positive")
        
        total_refunded = self._get_total_refunded(order)
        available_amount = order.total_amount - total_refunded
        
        if refund_amount > available_amount:
            raise InsufficientFundsError(
                f"Refund amount {refund_amount} exceeds available amount {available_amount}"
            )
    
    def _create_refund_transaction(self, order: Order, amount: Decimal, 
                                 reason: str) -> RefundTransaction:
        """Create a new refund transaction record."""
        return RefundTransaction.objects.create(
            order=order,
            amount=amount,
            reason=reason,
            status='pending',
            created_at=timezone.now()
        )
    
    def _process_gateway_refund(self, payment: Payment, amount: Decimal) -> Dict[str, Any]:
        """Process refund through payment gateway."""
        return self.payment_gateway.process_refund(
            transaction_id=payment.gateway_transaction_id,
            amount=amount
        )
    
    def _update_refund_transaction(self, refund_transaction: RefundTransaction, 
                                 gateway_response: Dict[str, Any]) -> None:
        """Update refund transaction with gateway response."""
        refund_transaction.gateway_transaction_id = gateway_response.get('transaction_id')
        refund_transaction.status = 'completed' if gateway_response.get('success') else 'failed'
        refund_transaction.gateway_response = gateway_response
        refund_transaction.processed_at = timezone.now()
        refund_transaction.save()
    
    def _update_order_totals(self, order: Order, refund_amount: Decimal) -> None:
        """Update order refund totals."""
        order.total_refunded = (order.total_refunded or Decimal('0.00')) + refund_amount
        order.save()
    
    def _get_total_refunded(self, order: Order) -> Decimal:
        """Calculate total amount already refunded for an order."""
        return order.refund_transactions.filter(
            status='completed'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
    
    def _get_payment_gateway(self):
        """Get configured payment gateway instance."""
        from .gateways import PaymentGatewayFactory
        return PaymentGatewayFactory.get_default_gateway()