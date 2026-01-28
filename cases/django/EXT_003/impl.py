from decimal import Decimal
from typing import Optional, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
import logging

from .models import Order, OrderItem, PaymentTransaction
from .payment_gateway import PaymentGateway
from .inventory_service import InventoryService
from .notification_service import NotificationService

logger = logging.getLogger(__name__)


class OrderProcessingService:
    
    def __init__(self):
        self.payment_gateway = PaymentGateway()
        self.inventory_service = InventoryService()
        self.notification_service = NotificationService()
    
    def process_order(self, order_id: int, payment_method: str) -> Dict[str, Any]:
        try:
            with transaction.atomic():
                order = self._get_and_validate_order(order_id)
                self._reserve_inventory(order)
                self._update_order_status(order, 'processing')
                
                payment_result = self._charge_payment(order, payment_method)
                
                if not payment_result['success']:
                    raise ValidationError(f"Payment failed: {payment_result['error']}")
                
                self._create_payment_record(order, payment_result)
                self._update_order_status(order, 'confirmed')
                
                return {
                    'success': True,
                    'order_id': order.id,
                    'payment_id': payment_result['transaction_id'],
                    'total_amount': order.total_amount
                }
                
        except Exception as e:
            logger.error(f"Order processing failed for order {order_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_and_validate_order(self, order_id: int) -> Order:
        try:
            order = Order.objects.select_for_update().get(id=order_id)
        except Order.DoesNotExist:
            raise ValidationError(f"Order {order_id} not found")
        
        if order.status != 'pending':
            raise ValidationError(f"Order {order_id} is not in pending status")
        
        if order.total_amount <= 0:
            raise ValidationError("Order total must be greater than zero")
        
        return order
    
    def _reserve_inventory(self, order: Order) -> None:
        for item in order.items.all():
            if not self.inventory_service.reserve_item(item.product_id, item.quantity):
                raise ValidationError(f"Insufficient inventory for product {item.product_id}")
    
    def _charge_payment(self, order: Order, payment_method: str) -> Dict[str, Any]:
        payment_data = {
            'amount': order.total_amount,
            'currency': 'USD',
            'payment_method': payment_method,
            'order_reference': f"ORDER-{order.id}",
            'customer_id': order.customer_id
        }
        
        return self.payment_gateway.charge(payment_data)
    
    def _create_payment_record(self, order: Order, payment_result: Dict[str, Any]) -> PaymentTransaction:
        return PaymentTransaction.objects.create(
            order=order,
            transaction_id=payment_result['transaction_id'],
            amount=order.total_amount,
            payment_method=payment_result['payment_method'],
            status='completed',
            processed_at=timezone.now()
        )
    
    def _update_order_status(self, order: Order, status: str) -> None:
        order.status = status
        order.updated_at = timezone.now()
        order.save(update_fields=['status', 'updated_at'])