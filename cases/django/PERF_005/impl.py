from typing import List, Optional, Dict, Any
from decimal import Decimal
from django.db import transaction
from django.db.models import QuerySet, Q, Sum, Count
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Order, OrderItem, Customer


class OrderAnalyticsService:
    """Service for analyzing order data and generating business insights."""
    
    def __init__(self):
        self.cache_timeout = 300
        
    def get_orders_by_status(self, status: str, limit: Optional[int] = None) -> QuerySet:
        """Retrieve orders filtered by status with optional limit."""
        queryset = Order.objects.filter(status=status).select_related('customer')
        if limit:
            queryset = queryset[:limit]
        return queryset
    
    def analyze_order_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analyze order trends over specified number of days."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        pending_orders = self._get_status_count('pending', start_date, end_date)
        processing_orders = self._get_status_count('processing', start_date, end_date)
        completed_orders = self._get_status_count('completed', start_date, end_date)
        cancelled_orders = self._get_status_count('cancelled', start_date, end_date)
        
        total_revenue = self._calculate_revenue_by_status('completed', start_date, end_date)
        
        return {
            'period_days': days,
            'status_breakdown': {
                'pending': pending_orders,
                'processing': processing_orders,
                'completed': completed_orders,
                'cancelled': cancelled_orders
            },
            'total_revenue': total_revenue,
            'conversion_rate': self._calculate_conversion_rate(start_date, end_date)
        }
    
    def _get_status_count(self, status: str, start_date: datetime, end_date: datetime) -> int:
        """Get count of orders with specific status in date range."""
        return Order.objects.filter(
            status=status,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).count()
    
    def _calculate_revenue_by_status(self, status: str, start_date: datetime, end_date: datetime) -> Decimal:
        """Calculate total revenue for orders with specific status."""
        orders = Order.objects.filter(
            status=status,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        total = orders.aggregate(revenue=Sum('total_amount'))['revenue']
        return total or Decimal('0.00')
    
    def _calculate_conversion_rate(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate order conversion rate from pending to completed."""
        total_orders = Order.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).count()
        
        completed_orders = self._get_status_count('completed', start_date, end_date)
        
        if total_orders == 0:
            return 0.0
        
        return round((completed_orders / total_orders) * 100, 2)
    
    @transaction.atomic
    def bulk_update_order_status(self, order_ids: List[int], new_status: str) -> int:
        """Update status for multiple orders in a single transaction."""
        if not self._is_valid_status(new_status):
            raise ValidationError(f"Invalid status: {new_status}")
        
        updated_count = Order.objects.filter(
            id__in=order_ids,
            status__in=['pending', 'processing']
        ).update(
            status=new_status,
            updated_at=timezone.now()
        )
        
        return updated_count
    
    def _is_valid_status(self, status: str) -> bool:
        """Validate if the provided status is allowed."""
        valid_statuses = ['pending', 'processing', 'completed', 'cancelled', 'refunded']
        return status in valid_statuses