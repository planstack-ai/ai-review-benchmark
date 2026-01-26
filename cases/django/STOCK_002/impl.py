from decimal import Decimal
from typing import Optional, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Product, Order, OrderItem
from .exceptions import InsufficientStockError, ProductNotFoundError


class StockManagementService:
    """Service for managing product stock operations."""
    
    def __init__(self):
        self.minimum_stock_threshold = 5
    
    def reserve_stock(self, product_id: int, quantity: int, order_id: Optional[int] = None) -> bool:
        """Reserve stock for a product with the specified quantity."""
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")
        
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")
        
        return self._process_stock_reservation(product, quantity, order_id)
    
    def _process_stock_reservation(self, product: Product, quantity: int, order_id: Optional[int]) -> bool:
        """Process the actual stock reservation logic."""
        if not self._validate_stock_availability(product, quantity):
            raise InsufficientStockError(
                f"Insufficient stock for product {product.name}. "
                f"Available: {product.stock}, Requested: {quantity}"
            )
        
        self._update_product_stock(product, quantity)
        
        if order_id:
            self._create_stock_reservation_record(product, quantity, order_id)
        
        return True
    
    def _validate_stock_availability(self, product: Product, quantity: int) -> bool:
        """Validate if sufficient stock is available for reservation."""
        return product.stock >= quantity
    
    def _update_product_stock(self, product: Product, quantity: int) -> None:
        """Update the product stock by decrementing the reserved quantity."""
        if product.stock >= quantity:
            product.stock -= quantity
            product.last_updated = timezone.now()
            product.save()
            
            if product.stock <= self.minimum_stock_threshold:
                self._trigger_low_stock_alert(product)
    
    def _create_stock_reservation_record(self, product: Product, quantity: int, order_id: int) -> None:
        """Create a record of the stock reservation for audit purposes."""
        from .models import StockReservation
        
        StockReservation.objects.create(
            product=product,
            order_id=order_id,
            quantity=quantity,
            reserved_at=timezone.now(),
            status='reserved'
        )
    
    def _trigger_low_stock_alert(self, product: Product) -> None:
        """Trigger alert when stock falls below minimum threshold."""
        from .tasks import send_low_stock_notification
        send_low_stock_notification.delay(product.id)
    
    def bulk_reserve_stock(self, reservations: Dict[int, int], order_id: Optional[int] = None) -> Dict[int, bool]:
        """Reserve stock for multiple products in a single operation."""
        results = {}
        
        for product_id, quantity in reservations.items():
            try:
                results[product_id] = self.reserve_stock(product_id, quantity, order_id)
            except (InsufficientStockError, ProductNotFoundError, ValidationError):
                results[product_id] = False
        
        return results
    
    def get_stock_status(self, product_id: int) -> Dict[str, Any]:
        """Get current stock status for a product."""
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            return {
                'product_id': product_id,
                'current_stock': product.stock,
                'is_low_stock': product.stock <= self.minimum_stock_threshold,
                'last_updated': product.last_updated
            }
        except Product.DoesNotExist:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")