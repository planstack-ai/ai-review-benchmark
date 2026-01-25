from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from typing import List, Optional, Dict, Any
from django.core.exceptions import ValidationError
from .models import Order, OrderItem, Product


class OrderProcessingService:
    """Service for processing and managing order lifecycle operations."""
    
    def __init__(self):
        self.processing_fee = Decimal('2.50')
        self.bulk_discount_threshold = 10
    
    def process_bulk_order_status_update(self, order_ids: List[int], new_status: str) -> Dict[str, Any]:
        """Process bulk status updates for multiple orders efficiently."""
        if not order_ids:
            raise ValidationError("Order IDs list cannot be empty")
        
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled', 'archived']
        if new_status not in valid_statuses:
            raise ValidationError(f"Invalid status: {new_status}")
        
        orders_queryset = Order.objects.filter(id__in=order_ids, is_active=True)
        initial_count = orders_queryset.count()
        
        if initial_count == 0:
            return {'updated_count': 0, 'skipped_count': len(order_ids)}
        
        with transaction.atomic():
            self._validate_status_transition(orders_queryset, new_status)
            
            updated_count = orders_queryset.update(
                status=new_status,
                updated_at=timezone.now(),
                last_modified_by='system'
            )
            
            if new_status == 'archived':
                self._handle_archived_orders_cleanup(order_ids)
            
            self._log_bulk_status_change(order_ids, new_status, updated_count)
        
        return {
            'updated_count': updated_count,
            'skipped_count': len(order_ids) - updated_count,
            'processing_timestamp': timezone.now()
        }
    
    def archive_completed_orders(self, days_threshold: int = 30) -> int:
        """Archive orders that have been completed for specified days."""
        cutoff_date = timezone.now() - timezone.timedelta(days=days_threshold)
        
        completed_orders = Order.objects.filter(
            status='delivered',
            completed_at__lt=cutoff_date,
            is_active=True
        )
        
        archived_count = completed_orders.update(
            status='archived',
            archived_at=timezone.now(),
            is_active=False
        )
        
        return archived_count
    
    def _validate_status_transition(self, orders_queryset, target_status: str) -> None:
        """Validate that status transitions are allowed for all orders."""
        invalid_transitions = []
        
        for order in orders_queryset.select_related():
            if not self._is_valid_transition(order.status, target_status):
                invalid_transitions.append(f"Order {order.id}: {order.status} -> {target_status}")
        
        if invalid_transitions:
            raise ValidationError(f"Invalid status transitions: {', '.join(invalid_transitions)}")
    
    def _is_valid_transition(self, current_status: str, target_status: str) -> bool:
        """Check if status transition is valid according to business rules."""
        transition_rules = {
            'pending': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': ['archived'],
            'cancelled': ['archived'],
            'archived': []
        }
        
        return target_status in transition_rules.get(current_status, [])
    
    def _handle_archived_orders_cleanup(self, order_ids: List[int]) -> None:
        """Handle cleanup tasks when orders are archived."""
        OrderItem.objects.filter(order_id__in=order_ids).update(is_active=False)
        
        self._update_product_inventory_tracking(order_ids)
    
    def _update_product_inventory_tracking(self, order_ids: List[int]) -> None:
        """Update product inventory tracking for archived orders."""
        order_items = OrderItem.objects.filter(
            order_id__in=order_ids
        ).select_related('product')
        
        for item in order_items:
            if item.product:
                item.product.reserved_quantity -= item.quantity
                item.product.save()
    
    def _log_bulk_status_change(self, order_ids: List[int], status: str, count: int) -> None:
        """Log bulk status change operation for audit purposes."""
        from django.contrib.admin.models import LogEntry, CHANGE
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(Order)
        
        LogEntry.objects.create(
            content_type=content_type,
            object_id=None,
            object_repr=f"Bulk update: {count} orders to {status}",
            action_flag=CHANGE,
            change_message=f"Bulk status update for orders: {order_ids[:10]}"
        )