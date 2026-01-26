from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError


class SalePeriodService:
    """Service for managing sale periods and pricing calculations."""
    
    def __init__(self):
        self.active_sales_cache = {}
    
    def is_sale_active(self, sale_id: int) -> bool:
        """Check if a sale is currently active based on its period boundaries."""
        from .models import Sale
        
        try:
            sale = Sale.objects.get(id=sale_id, is_enabled=True)
            return self._is_within_sale_period(sale)
        except Sale.DoesNotExist:
            return False
    
    def get_active_sales_for_product(self, product_id: int) -> List[dict]:
        """Retrieve all active sales for a specific product."""
        from .models import Sale
        
        current_time = timezone.now()
        active_sales = []
        
        sales = Sale.objects.filter(
            products__id=product_id,
            is_enabled=True
        ).select_related('discount_rule')
        
        for sale in sales:
            if self._is_within_sale_period(sale):
                active_sales.append({
                    'id': sale.id,
                    'name': sale.name,
                    'discount_percentage': sale.discount_rule.percentage,
                    'start_date': sale.start_date,
                    'end_date': sale.end_date
                })
        
        return active_sales
    
    def calculate_sale_price(self, original_price: Decimal, product_id: int) -> Decimal:
        """Calculate the final price after applying active sale discounts."""
        active_sales = self.get_active_sales_for_product(product_id)
        
        if not active_sales:
            return original_price
        
        best_discount = max(sale['discount_percentage'] for sale in active_sales)
        discount_amount = original_price * (best_discount / Decimal('100'))
        
        return original_price - discount_amount
    
    @transaction.atomic
    def create_sale_period(self, name: str, start_date: date, end_date: date, 
                          product_ids: List[int], discount_percentage: Decimal) -> int:
        """Create a new sale period with specified parameters."""
        from .models import Sale, DiscountRule, Product
        
        self._validate_sale_period(start_date, end_date)
        
        discount_rule = DiscountRule.objects.create(
            percentage=discount_percentage,
            rule_type='percentage'
        )
        
        sale = Sale.objects.create(
            name=name,
            start_date=start_date,
            end_date=end_date,
            discount_rule=discount_rule,
            is_enabled=True
        )
        
        products = Product.objects.filter(id__in=product_ids)
        sale.products.set(products)
        
        return sale.id
    
    def _is_within_sale_period(self, sale) -> bool:
        """Check if current datetime falls within the sale period boundaries."""
        current_time = timezone.now()
        
        start_datetime = datetime.combine(sale.start_date, current_time.time())
        end_datetime = datetime.combine(sale.end_date, time(23, 59, 59))
        
        return start_datetime <= current_time <= end_datetime
    
    def _validate_sale_period(self, start_date: date, end_date: date) -> None:
        """Validate that the sale period dates are logical."""
        if start_date >= end_date:
            raise ValidationError("Sale start date must be before end date")
        
        if start_date < timezone.now().date():
            raise ValidationError("Sale start date cannot be in the past")
    
    def _clear_sales_cache(self) -> None:
        """Clear the internal sales cache."""
        self.active_sales_cache.clear()