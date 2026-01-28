from decimal import Decimal
from typing import List, Optional, Dict, Any
from django.db import transaction
from django.db.models import QuerySet, Q, Sum
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Order, OrderItem, User
from .exceptions import OrderProcessingError, InsufficientInventoryError


class OrderAnalyticsService:
    """Service for analyzing order data and generating reports."""
    
    def __init__(self):
        self.cache_timeout = 300
        
    def get_user_order_summary(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive order summary for a specific user."""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        orders = Order.objects.select_related('user', 'items', 'payments', 'shipments').filter(
            user_id=user_id,
            created_at__gte=cutoff_date
        ).order_by('-created_at')
        
        return self._calculate_order_metrics(orders, user_id)
    
    def get_top_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve top customers by order value in the last quarter."""
        cutoff_date = timezone.now() - timezone.timedelta(days=90)
        
        orders = Order.objects.select_related('user', 'items', 'payments', 'shipments').filter(
            created_at__gte=cutoff_date,
            status__in=['completed', 'shipped']
        )
        
        customer_data = {}
        for order in orders:
            user_id = order.user.id
            if user_id not in customer_data:
                customer_data[user_id] = {
                    'user_name': order.user.get_full_name(),
                    'email': order.user.email,
                    'total_spent': Decimal('0.00'),
                    'order_count': 0
                }
            
            customer_data[user_id]['total_spent'] += order.total_amount
            customer_data[user_id]['order_count'] += 1
        
        return sorted(
            customer_data.values(),
            key=lambda x: x['total_spent'],
            reverse=True
        )[:limit]
    
    def analyze_order_patterns(self, start_date: timezone.datetime, 
                             end_date: timezone.datetime) -> Dict[str, Any]:
        """Analyze ordering patterns within a date range."""
        orders = Order.objects.select_related('user', 'items', 'payments', 'shipments').filter(
            created_at__range=(start_date, end_date)
        )
        
        patterns = {
            'total_orders': orders.count(),
            'average_order_value': self._calculate_average_order_value(orders),
            'peak_hours': self._identify_peak_ordering_hours(orders),
            'user_segments': self._segment_users_by_behavior(orders)
        }
        
        return patterns
    
    def _calculate_order_metrics(self, orders: QuerySet, user_id: int) -> Dict[str, Any]:
        """Calculate detailed metrics for a set of orders."""
        total_spent = sum(order.total_amount for order in orders)
        order_count = orders.count()
        
        return {
            'user_id': user_id,
            'total_orders': order_count,
            'total_spent': total_spent,
            'average_order_value': total_spent / order_count if order_count > 0 else Decimal('0.00'),
            'last_order_date': orders.first().created_at if orders.exists() else None,
            'order_frequency': self._calculate_order_frequency(orders)
        }
    
    def _calculate_average_order_value(self, orders: QuerySet) -> Decimal:
        """Calculate the average order value from a queryset."""
        if not orders.exists():
            return Decimal('0.00')
        
        total_value = sum(order.total_amount for order in orders)
        return total_value / orders.count()
    
    def _identify_peak_ordering_hours(self, orders: QuerySet) -> List[int]:
        """Identify the hours of day with highest order volume."""
        hour_counts = {}
        
        for order in orders:
            hour = order.created_at.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        return [hour for hour, count in sorted_hours[:3]]
    
    def _segment_users_by_behavior(self, orders: QuerySet) -> Dict[str, int]:
        """Segment users based on their ordering behavior."""
        user_order_counts = {}
        
        for order in orders:
            user_id = order.user.id
            user_order_counts[user_id] = user_order_counts.get(user_id, 0) + 1
        
        segments = {'high_frequency': 0, 'medium_frequency': 0, 'low_frequency': 0}
        
        for count in user_order_counts.values():
            if count >= 10:
                segments['high_frequency'] += 1
            elif count >= 3:
                segments['medium_frequency'] += 1
            else:
                segments['low_frequency'] += 1
        
        return segments
    
    def _calculate_order_frequency(self, orders: QuerySet) -> Optional[float]:
        """Calculate average days between orders for a user."""
        if orders.count() < 2:
            return None
        
        order_dates = [order.created_at for order in orders.order_by('created_at')]
        total_days = (order_dates[-1] - order_dates[0]).days
        
        return total_days / (len(order_dates) - 1) if total_days > 0 else 0.0