from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import Optional, Dict, Any
from .models import Product, StockMovement, Order


class StockManagementService:
    """Service for managing product stock levels and movements."""
    
    def __init__(self):
        self.minimum_stock_level = Decimal('0.00')
    
    def process_order_cancellation(self, order_id: int) -> Dict[str, Any]:
        """Process order cancellation and restore stock levels."""
        with transaction.atomic():
            try:
                order = Order.objects.select_for_update().get(id=order_id)
                if order.status != 'confirmed':
                    raise ValidationError("Only confirmed orders can be cancelled")
                
                restoration_summary = self._restore_cancelled_stock(order)
                order.status = 'cancelled'
                order.save()
                
                return {
                    'success': True,
                    'order_id': order_id,
                    'restored_items': restoration_summary
                }
            except Order.DoesNotExist:
                raise ValidationError(f"Order {order_id} not found")
    
    def _restore_cancelled_stock(self, order) -> Dict[str, Decimal]:
        """Restore stock for cancelled order items."""
        restoration_summary = {}
        
        for item in order.items.all():
            product = Product.objects.select_for_update().get(id=item.product_id)
            cancelled_quantity = item.quantity
            
            previous_stock = product.stock_quantity
            product.stock_quantity += cancelled_quantity
            
            if self._validate_stock_constraints(product):
                product.save()
                self._create_stock_movement(
                    product=product,
                    quantity=cancelled_quantity,
                    movement_type='cancellation_restore',
                    reference_id=order.id
                )
                restoration_summary[product.sku] = cancelled_quantity
            else:
                raise ValidationError(f"Stock restoration failed for {product.sku}")
        
        return restoration_summary
    
    def _validate_stock_constraints(self, product) -> bool:
        """Validate that stock levels meet business constraints."""
        if product.stock_quantity < self.minimum_stock_level:
            return False
        
        if hasattr(product, 'max_stock_level') and product.max_stock_level:
            if product.stock_quantity > product.max_stock_level:
                return False
        
        return True
    
    def _create_stock_movement(self, product, quantity: Decimal, 
                             movement_type: str, reference_id: Optional[int] = None):
        """Create a stock movement record for audit purposes."""
        StockMovement.objects.create(
            product=product,
            quantity=quantity,
            movement_type=movement_type,
            reference_id=reference_id,
            resulting_stock=product.stock_quantity
        )
    
    def get_stock_level(self, product_id: int) -> Decimal:
        """Get current stock level for a product."""
        try:
            product = Product.objects.get(id=product_id)
            return product.stock_quantity
        except Product.DoesNotExist:
            raise ValidationError(f"Product {product_id} not found")
    
    def check_stock_availability(self, product_id: int, required_quantity: Decimal) -> bool:
        """Check if sufficient stock is available for a given quantity."""
        current_stock = self.get_stock_level(product_id)
        return current_stock >= required_quantity