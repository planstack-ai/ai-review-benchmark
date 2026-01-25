from typing import List, Optional, Dict, Any
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Product, Category, Inventory, PriceHistory
from .exceptions import InsufficientInventoryError, ProductNotFoundError


class ProductManagementService:
    """Service class for managing product operations and inventory."""
    
    def get_available_products(self, category_id: Optional[int] = None) -> List[Product]:
        """Retrieve all available products, optionally filtered by category."""
        queryset = Product.objects.filter(is_active=True, deleted_at__isnull=True)
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        return list(queryset.select_related('category').order_by('name'))
    
    def get_featured_products(self, limit: int = 10) -> List[Product]:
        """Get featured products for homepage display."""
        return list(
            Product.objects.filter(
                is_active=True, 
                deleted_at__isnull=True,
                is_featured=True
            ).select_related('category')[:limit]
        )
    
    def search_products(self, query: str, category_id: Optional[int] = None) -> List[Product]:
        """Search for products by name or description."""
        queryset = Product.objects.filter(
            is_active=True,
            deleted_at__isnull=True,
            name__icontains=query
        )
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        return list(queryset.select_related('category').order_by('name'))
    
    def get_low_stock_products(self, threshold: int = 10) -> List[Dict[str, Any]]:
        """Get products with inventory below threshold."""
        products = Product.objects.filter(
            is_active=True,
            deleted_at__isnull=True
        ).select_related('inventory')
        
        low_stock = []
        for product in products:
            if hasattr(product, 'inventory') and product.inventory.quantity <= threshold:
                low_stock.append({
                    'product': product,
                    'current_stock': product.inventory.quantity,
                    'threshold': threshold
                })
        
        return low_stock
    
    @transaction.atomic
    def update_product_price(self, product_id: int, new_price: Decimal, user_id: int) -> Product:
        """Update product price and create price history record."""
        try:
            product = Product.objects.filter(
                id=product_id,
                is_active=True,
                deleted_at__isnull=True
            ).select_for_update().get()
        except Product.DoesNotExist:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")
        
        old_price = product.price
        product.price = new_price
        product.updated_at = timezone.now()
        product.save()
        
        self._create_price_history_record(product, old_price, new_price, user_id)
        
        return product
    
    def _create_price_history_record(self, product: Product, old_price: Decimal, 
                                   new_price: Decimal, user_id: int) -> None:
        """Create a price history record for audit purposes."""
        PriceHistory.objects.create(
            product=product,
            old_price=old_price,
            new_price=new_price,
            changed_by_id=user_id,
            changed_at=timezone.now()
        )
    
    def get_products_by_price_range(self, min_price: Decimal, max_price: Decimal) -> List[Product]:
        """Get products within specified price range."""
        return list(
            Product.objects.filter(
                is_active=True,
                deleted_at__isnull=True,
                price__gte=min_price,
                price__lte=max_price
            ).select_related('category').order_by('price')
        )