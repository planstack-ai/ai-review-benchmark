from decimal import Decimal
from typing import Optional, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Product, PriceHistory
from .exceptions import ProductNotFoundError, InvalidPriceError


class ProductPricingService:
    """Service for managing product pricing with history tracking."""
    
    def __init__(self):
        self.minimum_price = Decimal('0.01')
        self.maximum_discount_percent = Decimal('75.00')
    
    def update_product_price(self, product_id: int, new_price: Decimal, 
                           updated_by: str, reason: str = '') -> Product:
        """Update product price with validation and history tracking."""
        product = self._get_product(product_id)
        
        if not self._is_valid_price(new_price):
            raise InvalidPriceError(f"Invalid price: {new_price}")
        
        old_price = product.price
        discount_percent = self._calculate_discount_percent(old_price, new_price)
        
        if discount_percent > self.maximum_discount_percent:
            raise ValidationError(f"Discount exceeds maximum allowed: {discount_percent}%")
        
        return self._apply_price_update(product, new_price, old_price, updated_by, reason)
    
    def bulk_update_prices(self, price_updates: Dict[int, Decimal], 
                          updated_by: str) -> Dict[int, Product]:
        """Update multiple product prices in a single transaction."""
        results = {}
        
        with transaction.atomic():
            for product_id, new_price in price_updates.items():
                try:
                    updated_product = self.update_product_price(
                        product_id, new_price, updated_by, 'Bulk price update'
                    )
                    results[product_id] = updated_product
                except (ProductNotFoundError, InvalidPriceError, ValidationError):
                    continue
        
        return results
    
    def get_price_history(self, product_id: int, limit: int = 10) -> list:
        """Retrieve price change history for a product."""
        product = self._get_product(product_id)
        return list(product.price_history.order_by('-created_at')[:limit])
    
    def _get_product(self, product_id: int) -> Product:
        """Retrieve product by ID or raise exception if not found."""
        try:
            return Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")
    
    def _is_valid_price(self, price: Decimal) -> bool:
        """Validate price is within acceptable range."""
        return price >= self.minimum_price and price <= Decimal('999999.99')
    
    def _calculate_discount_percent(self, old_price: Decimal, new_price: Decimal) -> Decimal:
        """Calculate discount percentage between old and new price."""
        if old_price <= 0:
            return Decimal('0.00')
        
        discount = old_price - new_price
        if discount <= 0:
            return Decimal('0.00')
        
        return (discount / old_price) * Decimal('100.00')
    
    def _apply_price_update(self, product: Product, new_price: Decimal, 
                           old_price: Decimal, updated_by: str, reason: str) -> Product:
        """Apply the price update and create history record."""
        with transaction.atomic():
            product.price = new_price
            product.last_updated = timezone.now()
            product.save()
            
            self._create_price_history_record(
                product, old_price, new_price, updated_by, reason
            )
        
        return product
    
    def _create_price_history_record(self, product: Product, old_price: Decimal,
                                   new_price: Decimal, updated_by: str, reason: str) -> None:
        """Create a price history record for audit purposes."""
        PriceHistory.objects.create(
            product=product,
            old_price=old_price,
            new_price=new_price,
            updated_by=updated_by,
            reason=reason,
            created_at=timezone.now()
        )