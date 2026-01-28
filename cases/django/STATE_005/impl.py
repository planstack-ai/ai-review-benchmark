from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import List, Optional
from .models import Order, OrderItem


class OrderCancellationService:
    """Service for handling order and item cancellations with integrity checks."""
    
    def __init__(self, order: Order):
        self.order = order
        self._original_total = order.total_amount
    
    def partial_cancel_items(self, item_ids: List[int], reason: str = "") -> bool:
        """Cancel specific items from an order and update totals."""
        if not self._validate_cancellation_request(item_ids):
            return False
            
        with transaction.atomic():
            cancelled_items = self._process_item_cancellations(item_ids, reason)
            if not cancelled_items:
                return False
                
            self._update_order_status()
            self._log_cancellation_activity(cancelled_items, reason)
            
        return True
    
    def full_cancel_order(self, reason: str = "") -> bool:
        """Cancel entire order and all associated items."""
        with transaction.atomic():
            item_ids = list(self.order.items.filter(status='active').values_list('id', flat=True))
            
            if not item_ids:
                return False
                
            self._process_item_cancellations(item_ids, reason)
            self.order.status = 'cancelled'
            self.order.total_amount = Decimal('0.00')
            self.order.save()
            
        return True
    
    def _validate_cancellation_request(self, item_ids: List[int]) -> bool:
        """Validate that items can be cancelled."""
        if not item_ids:
            return False
            
        valid_items = self.order.items.filter(
            id__in=item_ids,
            status='active'
        ).count()
        
        return valid_items == len(item_ids)
    
    def _process_item_cancellations(self, item_ids: List[int], reason: str) -> List[OrderItem]:
        """Process the actual cancellation of items."""
        items_to_cancel = self.order.items.filter(
            id__in=item_ids,
            status='active'
        )
        
        cancelled_items = []
        for item in items_to_cancel:
            item.status = 'cancelled'
            item.cancellation_reason = reason
            item.save()
            cancelled_items.append(item)
            
        return cancelled_items
    
    def _update_order_status(self) -> None:
        """Update order status based on remaining active items."""
        active_items_count = self.order.items.filter(status='active').count()
        
        if active_items_count == 0:
            self.order.status = 'cancelled'
        elif active_items_count < self.order.items.count():
            self.order.status = 'partially_cancelled'
            
        self.order.save()
    
    def _log_cancellation_activity(self, cancelled_items: List[OrderItem], reason: str) -> None:
        """Log cancellation activity for audit purposes."""
        from .models import OrderActivity
        
        total_cancelled_amount = sum(item.total_price for item in cancelled_items)
        
        OrderActivity.objects.create(
            order=self.order,
            activity_type='partial_cancellation',
            description=f"Cancelled {len(cancelled_items)} items. Amount: ${total_cancelled_amount}",
            reason=reason
        )