from decimal import Decimal
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from orders.models import Order, OrderItem
import logging

logger = logging.getLogger(__name__)


class OrderBatchProcessingService:
    """Service for processing orders in batches with full table load capability."""
    
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self.processed_count = 0
        self.error_count = 0
    
    def process_all_orders(self, status_filter: Optional[str] = None) -> Dict[str, Any]:
        """Process all orders in the system with optional status filtering."""
        start_time = timezone.now()
        
        try:
            orders = self._load_orders(status_filter)
            total_orders = len(orders)
            
            logger.info(f"Starting batch processing of {total_orders} orders")
            
            batches = self._create_batches(orders)
            
            for batch_index, batch in enumerate(batches):
                try:
                    self._process_batch(batch, batch_index + 1)
                except Exception as e:
                    logger.error(f"Error processing batch {batch_index + 1}: {str(e)}")
                    self.error_count += len(batch)
            
            end_time = timezone.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return {
                'total_orders': total_orders,
                'processed_count': self.processed_count,
                'error_count': self.error_count,
                'processing_time_seconds': processing_time,
                'success_rate': (self.processed_count / total_orders) * 100 if total_orders > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Critical error in order processing: {str(e)}")
            raise
    
    def _load_orders(self, status_filter: Optional[str] = None) -> List[Order]:
        """Load orders from database with optional filtering."""
        queryset = Order.objects.select_related('customer').prefetch_related('items')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return list(queryset.all())
    
    def _create_batches(self, orders: List[Order]) -> List[List[Order]]:
        """Split orders into processing batches."""
        batches = []
        for i in range(0, len(orders), self.batch_size):
            batch = orders[i:i + self.batch_size]
            batches.append(batch)
        return batches
    
    @transaction.atomic
    def _process_batch(self, batch: List[Order], batch_number: int) -> None:
        """Process a single batch of orders."""
        logger.info(f"Processing batch {batch_number} with {len(batch)} orders")
        
        for order in batch:
            try:
                self._process_single_order(order)
                self.processed_count += 1
            except ValidationError as e:
                logger.warning(f"Validation error for order {order.id}: {str(e)}")
                self.error_count += 1
            except Exception as e:
                logger.error(f"Unexpected error processing order {order.id}: {str(e)}")
                self.error_count += 1
    
    def _process_single_order(self, order: Order) -> None:
        """Process individual order with business logic."""
        if not self._validate_order(order):
            raise ValidationError(f"Order {order.id} failed validation")
        
        total_amount = self._calculate_order_total(order)
        
        if order.total != total_amount:
            order.total = total_amount
            order.save(update_fields=['total'])
        
        self._update_order_status(order)
    
    def _validate_order(self, order: Order) -> bool:
        """Validate order data integrity."""
        if not order.customer:
            return False
        
        if not order.items.exists():
            return False
        
        return True
    
    def _calculate_order_total(self, order: Order) -> Decimal:
        """Calculate total amount for order items."""
        total = Decimal('0.00')
        for item in order.items.all():
            total += item.quantity * item.unit_price
        return total
    
    def _update_order_status(self, order: Order) -> None:
        """Update order status based on business rules."""
        if order.status == 'pending' and order.total > Decimal('0.00'):
            order.status = 'processed'
            order.processed_at = timezone.now()
            order.save(update_fields=['status', 'processed_at'])