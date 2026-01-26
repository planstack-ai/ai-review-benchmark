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
        """Process status updates for multiple orders efficiently."""
        if not order_ids:
            raise ValidationError("Order IDs list cannot be empty")
        
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled', 'archived']
        if new_status not in valid_statuses:
            raise ValidationError(f"Invalid status: {new_status}")
        
        orders_queryset = Order.objects.filter(id__in=order_ids, is_active=True)
        initial_count = orders_queryset.count()
        
        if initial_count == 0:
            return {'updated_count': 0, 'errors': ['No valid orders found']}
        
        with transaction.atomic():
            updated_count = self._update_order_statuses(orders_queryset, new_status)
            self._log_bulk_status_change(order_ids, new_status, updated_count)
            
            if new_status == 'archived':
                self._handle_archived_orders_cleanup(orders_queryset)
        
        return {
            'updated_count': updated_count,
            'total_processed': initial_count,
            'status': new_status,
            'timestamp': timezone.now()
        }
    
    def _update_order_statuses(self, orders_queryset, new_status: str) -> int:
        """Update order statuses using efficient bulk operations."""
        update_data = {
            'status': new_status,
            'updated_at': timezone.now()
        }
        
        if new_status == 'shipped':
            update_data['shipped_at'] = timezone.now()
        elif new_status == 'delivered':
            update_data['delivered_at'] = timezone.now()
        elif new_status == 'cancelled':
            update_data['cancelled_at'] = timezone.now()
        
        return orders_queryset.update(**update_data)
    
    def _handle_archived_orders_cleanup(self, orders_queryset) -> None:
        """Handle cleanup operations for archived orders."""
        archived_orders = orders_queryset.filter(status='archived')
        
        for order in archived_orders:
            self._cleanup_order_references(order)
            self._update_customer_statistics(order.customer_id)
    
    def _cleanup_order_references(self, order) -> None:
        """Clean up related references for archived orders."""
        OrderItem.objects.filter(order=order, is_temporary=True).delete()
        
        if hasattr(order, 'tracking_info'):
            order.tracking_info.is_active = False
            order.tracking_info.save()
    
    def _update_customer_statistics(self, customer_id: int) -> None:
        """Update customer order statistics after archiving."""
        from .models import Customer
        
        customer = Customer.objects.get(id=customer_id)
        active_orders_count = Order.objects.filter(
            customer=customer,
            is_active=True
        ).exclude(status='archived').count()
        
        customer.active_orders_count = active_orders_count
        customer.last_order_update = timezone.now()
        customer.save()
    
    def _log_bulk_status_change(self, order_ids: List[int], status: str, count: int) -> None:
        """Log bulk status change operations for audit purposes."""
        from .models import OrderStatusLog
        
        OrderStatusLog.objects.create(
            operation_type='bulk_update',
            order_ids=order_ids,
            new_status=status,
            affected_count=count,
            timestamp=timezone.now()
        )
    
    def calculate_processing_metrics(self, order_ids: List[int]) -> Dict[str, Any]:
        """Calculate processing metrics for given orders."""
        orders = Order.objects.filter(id__in=order_ids)
        
        total_value = sum(order.total_amount for order in orders)
        average_value = total_value / len(orders) if orders else Decimal('0')
        
        return {
            'total_orders': len(orders),
            'total_value': total_value,
            'average_value': average_value,
            'processing_fee_total': self.processing_fee * len(orders)
        }