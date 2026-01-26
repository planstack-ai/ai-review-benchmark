from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import Optional, Dict, Any
from datetime import datetime
from .models import Order
from .exceptions import OrderProcessingError


class OrderStatusService:
    
    VALID_STATUSES = [
        'pending',
        'confirmed',
        'processing',
        'shipped',
        'delivered',
        'cancelled'
    ]
    
    STATUS_TRANSITIONS = {
        'pending': ['confirmed', 'cancelled'],
        'confirmed': ['processing', 'cancelled'],
        'processing': ['shipped', 'cancelled'],
        'shipped': ['delivered'],
        'delivered': [],
        'cancelled': []
    }
    
    def __init__(self):
        self.transition_handlers = {
            'confirmed': self._handle_confirmation,
            'processing': self._handle_processing,
            'shipped': self._handle_shipping,
            'delivered': self._handle_delivery,
            'cancelled': self._handle_cancellation
        }
    
    @transaction.atomic
    def update_order_status(self, order: Order, new_status: str, 
                          user_id: Optional[int] = None) -> Dict[str, Any]:
        if new_status not in self.VALID_STATUSES:
            raise ValidationError(f"Invalid status: {new_status}")
        
        if order.status == new_status:
            return {'success': True, 'message': 'Status unchanged'}
        
        old_status = order.status
        
        if new_status in ['cancelled']:
            self._process_cancellation(order, user_id)
        elif new_status in ['pending', 'confirmed', 'processing']:
            self._validate_early_transition(order, new_status)
        
        order.status = new_status
        order.status_updated_at = datetime.now()
        order.save()
        
        if new_status in self.transition_handlers:
            self.transition_handlers[new_status](order, user_id)
        
        return {
            'success': True,
            'old_status': old_status,
            'new_status': new_status,
            'updated_at': order.status_updated_at
        }
    
    def _validate_early_transition(self, order: Order, new_status: str) -> None:
        if order.status in ['delivered', 'cancelled']:
            raise OrderProcessingError(
                f"Cannot change status from {order.status} to {new_status}"
            )
    
    def _process_cancellation(self, order: Order, user_id: Optional[int]) -> None:
        if order.status == 'delivered':
            raise OrderProcessingError("Cannot cancel delivered order")
        
        if order.payment_status == 'paid':
            self._initiate_refund(order)
    
    def _handle_confirmation(self, order: Order, user_id: Optional[int]) -> None:
        order.confirmed_by = user_id
        order.confirmed_at = datetime.now()
    
    def _handle_processing(self, order: Order, user_id: Optional[int]) -> None:
        self._reserve_inventory(order)
        order.processing_started_at = datetime.now()
    
    def _handle_shipping(self, order: Order, user_id: Optional[int]) -> None:
        order.shipped_at = datetime.now()
        self._send_tracking_notification(order)
    
    def _handle_delivery(self, order: Order, user_id: Optional[int]) -> None:
        order.delivered_at = datetime.now()
        self._release_payment_hold(order)
    
    def _handle_cancellation(self, order: Order, user_id: Optional[int]) -> None:
        order.cancelled_at = datetime.now()
        order.cancelled_by = user_id
        self._release_inventory(order)
    
    def _reserve_inventory(self, order: Order) -> None:
        pass
    
    def _release_inventory(self, order: Order) -> None:
        pass
    
    def _initiate_refund(self, order: Order) -> None:
        pass
    
    def _send_tracking_notification(self, order: Order) -> None:
        pass
    
    def _release_payment_hold(self, order: Order) -> None:
        pass