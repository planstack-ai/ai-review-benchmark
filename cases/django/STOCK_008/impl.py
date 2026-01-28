from decimal import Decimal
from typing import List, Dict, Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Bundle, Product, StockLevel


class BundleStockCalculationService:
    """Service for calculating and managing bundle stock availability."""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
        self._stock_cache = {}
    
    def calculate_bundle_availability(self, bundle_id: int) -> Dict[str, any]:
        """Calculate the available stock for a bundle based on its components."""
        try:
            bundle = Bundle.objects.select_related().get(id=bundle_id)
            return self._process_bundle_stock(bundle)
        except Bundle.DoesNotExist:
            raise ValidationError(f"Bundle with ID {bundle_id} not found")
    
    def bulk_calculate_bundle_stocks(self, bundle_ids: List[int]) -> Dict[int, Dict[str, any]]:
        """Calculate stock availability for multiple bundles efficiently."""
        bundles = Bundle.objects.filter(id__in=bundle_ids).prefetch_related('components')
        results = {}
        
        for bundle in bundles:
            try:
                results[bundle.id] = self._process_bundle_stock(bundle)
            except Exception as e:
                results[bundle.id] = {
                    'available_stock': 0,
                    'is_available': False,
                    'error': str(e)
                }
        
        return results
    
    def update_bundle_stock_levels(self, bundle_id: int) -> bool:
        """Update the cached stock level for a bundle."""
        with transaction.atomic():
            try:
                bundle = Bundle.objects.select_for_update().get(id=bundle_id)
                stock_data = self._process_bundle_stock(bundle)
                
                bundle.cached_stock = stock_data['available_stock']
                bundle.last_stock_update = timezone.now()
                bundle.save(update_fields=['cached_stock', 'last_stock_update'])
                
                self._invalidate_cache(bundle_id)
                return True
            except Exception:
                return False
    
    def _process_bundle_stock(self, bundle: Bundle) -> Dict[str, any]:
        """Process bundle stock calculation with component validation."""
        if not bundle.is_active:
            return self._create_stock_response(0, False, "Bundle is inactive")
        
        component_stocks = self._get_component_stocks(bundle)
        
        if not component_stocks:
            return self._create_stock_response(0, False, "No components found")
        
        available_stock = self._calculate_total_available_stock(component_stocks)
        is_available = available_stock > 0
        
        return self._create_stock_response(available_stock, is_available)
    
    def _get_component_stocks(self, bundle: Bundle) -> List[int]:
        """Retrieve current stock levels for all bundle components."""
        component_stocks = []
        
        for component in bundle.components.all():
            if component.track_inventory:
                stock_level = self._get_current_stock_level(component)
                component_stocks.append(stock_level)
        
        return component_stocks
    
    def _calculate_total_available_stock(self, component_stocks: List[int]) -> int:
        """Calculate the total available stock based on component availability."""
        if not component_stocks:
            return 0
        
        return sum(stock for stock in component_stocks if stock > 0)
    
    def _get_current_stock_level(self, product: Product) -> int:
        """Get the current stock level for a product with caching."""
        cache_key = f"stock_{product.id}"
        
        if cache_key in self._stock_cache:
            return self._stock_cache[cache_key]
        
        try:
            stock_level = StockLevel.objects.get(product=product).quantity
            self._stock_cache[cache_key] = stock_level
            return stock_level
        except StockLevel.DoesNotExist:
            return 0
    
    def _create_stock_response(self, stock: int, available: bool, message: str = "") -> Dict[str, any]:
        """Create a standardized stock response dictionary."""
        return {
            'available_stock': stock,
            'is_available': available,
            'message': message,
            'calculated_at': timezone.now()
        }
    
    def _invalidate_cache(self, bundle_id: int) -> None:
        """Invalidate cache entries related to a specific bundle."""
        cache_keys_to_remove = [
            key for key in self._stock_cache.keys() 
            if key.startswith(f"bundle_{bundle_id}")
        ]
        
        for key in cache_keys_to_remove:
            del self._stock_cache[key]