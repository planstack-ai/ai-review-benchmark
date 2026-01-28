from datetime import datetime, timedelta
from typing import Optional, List
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class DeliveryCalculationService:
    """Service for calculating delivery dates and business day operations."""
    
    def __init__(self):
        self.standard_delivery_days = getattr(settings, 'STANDARD_DELIVERY_DAYS', 5)
        self.express_delivery_days = getattr(settings, 'EXPRESS_DELIVERY_DAYS', 2)
        self.overnight_delivery_days = getattr(settings, 'OVERNIGHT_DELIVERY_DAYS', 1)
    
    def calculate_delivery_date(self, order_date: datetime, delivery_type: str = 'standard') -> datetime:
        """Calculate the expected delivery date based on order date and delivery type."""
        if not isinstance(order_date, datetime):
            raise ValueError("Order date must be a datetime object")
        
        business_days = self._get_delivery_days_for_type(delivery_type)
        return self._add_business_days(order_date, business_days)
    
    def calculate_estimated_delivery_range(self, order_date: datetime, 
                                         delivery_type: str = 'standard') -> tuple[datetime, datetime]:
        """Calculate a delivery date range with buffer for potential delays."""
        base_delivery_date = self.calculate_delivery_date(order_date, delivery_type)
        buffer_days = 1 if delivery_type == 'overnight' else 2
        
        earliest_date = base_delivery_date
        latest_date = self._add_business_days(base_delivery_date, buffer_days)
        
        return earliest_date, latest_date
    
    def get_delivery_cost_multiplier(self, delivery_type: str, distance_km: float) -> Decimal:
        """Calculate delivery cost multiplier based on type and distance."""
        base_multipliers = {
            'standard': Decimal('1.0'),
            'express': Decimal('1.5'),
            'overnight': Decimal('2.5')
        }
        
        base_multiplier = base_multipliers.get(delivery_type, Decimal('1.0'))
        
        if distance_km > 500:
            base_multiplier *= Decimal('1.3')
        elif distance_km > 100:
            base_multiplier *= Decimal('1.1')
        
        return base_multiplier
    
    def is_delivery_available_on_date(self, target_date: datetime, 
                                    order_date: datetime, 
                                    delivery_type: str = 'standard') -> bool:
        """Check if delivery is possible on a specific target date."""
        earliest_delivery = self.calculate_delivery_date(order_date, delivery_type)
        return target_date >= earliest_delivery
    
    def _get_delivery_days_for_type(self, delivery_type: str) -> int:
        """Get the number of business days required for each delivery type."""
        delivery_days_map = {
            'standard': self.standard_delivery_days,
            'express': self.express_delivery_days,
            'overnight': self.overnight_delivery_days
        }
        return delivery_days_map.get(delivery_type, self.standard_delivery_days)
    
    def _add_business_days(self, start_date: datetime, business_days: int) -> datetime:
        """Add business days to a given date."""
        if business_days <= 0:
            return start_date
        
        current_date = start_date
        days_added = 0
        
        while days_added < business_days:
            current_date = current_date + timedelta(days=1)
            days_added += 1
        
        return current_date
    
    def _is_business_day(self, date: datetime) -> bool:
        """Check if a given date is a business day."""
        return date.weekday() < 5