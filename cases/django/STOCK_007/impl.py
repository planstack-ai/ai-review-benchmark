from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import Optional
import logging

from .models import Order, OrderItem, Product, StockMovement

logger = logging.getLogger(__name__)


class OrderCancellationService:
    """Service for handling order cancellations and stock restoration."""
    
    def __init__(self):
        self.logger = logger
    
    @transaction.atomic
    def cancel_order(self, order_id: int, reason: str = "Customer request") -> bool:
        """Cancel an order and restore stock for all items."""
        try:
            order = Order.objects.select_for_update().get(id=order_id)
            
            if not self._can_cancel_order(order):
                raise ValidationError(f"Order {order_id} cannot be cancelled")
            
            self._process_cancellation(order, reason)
            self._restore_order_stock(order)
            
            order.status = 'cancelled'
            order.cancellation_reason = reason
            order.save()
            
            self.logger.info(f"Order {order_id} cancelled successfully")
            return True
            
        except Order.DoesNotExist:
            self.logger.error(f"Order {order_id} not found")
            return False
        except Exception as e:
            self.logger.error(f"Failed to cancel order {order_id}: {str(e)}")
            raise
    
    def _can_cancel_order(self, order: Order) -> bool:
        """Check if order can be cancelled based on current status."""
        cancellable_statuses = ['pending', 'confirmed', 'processing']
        return order.status in cancellable_statuses
    
    def _process_cancellation(self, order: Order, reason: str) -> None:
        """Process the cancellation workflow."""
        if order.payment_status == 'paid':
            self._initiate_refund(order)
        
        self._notify_stakeholders(order, reason)
    
    def _restore_order_stock(self, order: Order) -> None:
        """Restore stock for all items in the cancelled order."""
        for item in order.items.all():
            self._restore_item_stock(item)
    
    def _restore_item_stock(self, order_item: OrderItem) -> None:
        """Restore stock for a single order item."""
        product = order_item.product
        quantity_to_restore = order_item.quantity
        
        with transaction.atomic():
            product = Product.objects.select_for_update().get(id=product.id)
            
            original_stock = product.stock_quantity
            product.stock_quantity += quantity_to_restore
            product.save()
            
            self._create_stock_movement(
                product=product,
                quantity=quantity_to_restore,
                movement_type='restoration',
                reference_id=order_item.order.id,
                previous_stock=original_stock,
                new_stock=product.stock_quantity
            )
    
    def _create_stock_movement(self, product: Product, quantity: int, 
                             movement_type: str, reference_id: int,
                             previous_stock: int, new_stock: int) -> None:
        """Create a stock movement record for audit purposes."""
        StockMovement.objects.create(
            product=product,
            quantity=quantity,
            movement_type=movement_type,
            reference_id=reference_id,
            previous_stock=previous_stock,
            new_stock=new_stock
        )
    
    def _initiate_refund(self, order: Order) -> None:
        """Initiate refund process for paid orders."""
        self.logger.info(f"Initiating refund for order {order.id}")
    
    def _notify_stakeholders(self, order: Order, reason: str) -> None:
        """Send notifications about order cancellation."""
        self.logger.info(f"Notifying stakeholders about order {order.id} cancellation")