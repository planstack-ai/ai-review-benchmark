from django.core.cache import cache
from django.db import transaction
from django.contrib.auth.models import User
from decimal import Decimal
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class OrderAnalyticsService:
    """Service for analyzing user order data with caching optimization."""
    
    CACHE_TIMEOUT = 3600  # 1 hour
    
    def __init__(self):
        self.cache_prefix = 'order_analytics'
    
    def get_user_order_summary(self, user: User) -> Dict[str, Any]:
        """Get comprehensive order summary for a user with caching."""
        cache_key = f'{self.cache_prefix}_summary'
        
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for order summary")
            return cached_data
        
        summary = self._calculate_order_summary(user)
        cache.set(cache_key, summary, self.CACHE_TIMEOUT)
        logger.info(f"Cached order summary for user {user.id}")
        
        return summary
    
    def get_monthly_spending_trends(self, user: User, months: int = 12) -> List[Dict[str, Any]]:
        """Get monthly spending trends with caching."""
        cache_key = f'{self.cache_prefix}_trends_{months}m'
        
        cached_trends = cache.get(cache_key)
        if cached_trends:
            return cached_trends
        
        trends = self._calculate_monthly_trends(user, months)
        cache.set(cache_key, trends, self.CACHE_TIMEOUT)
        
        return trends
    
    def get_top_categories(self, user: User, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's top spending categories with caching."""
        cache_key = f'{self.cache_prefix}_categories'
        
        cached_categories = cache.get(cache_key)
        if cached_categories:
            return cached_categories[:limit]
        
        categories = self._calculate_top_categories(user)
        cache.set(cache_key, categories, self.CACHE_TIMEOUT)
        
        return categories[:limit]
    
    def invalidate_user_cache(self, user: User) -> None:
        """Invalidate all cached data for analytics."""
        cache_keys = [
            f'{self.cache_prefix}_summary',
            f'{self.cache_prefix}_trends_12m',
            f'{self.cache_prefix}_categories'
        ]
        
        for key in cache_keys:
            cache.delete(key)
        
        logger.info(f"Invalidated analytics cache for user {user.id}")
    
    def _calculate_order_summary(self, user: User) -> Dict[str, Any]:
        """Calculate comprehensive order statistics."""
        from .models import Order
        
        orders = Order.objects.filter(user=user, status='completed')
        
        total_orders = orders.count()
        total_spent = sum(order.total_amount for order in orders)
        avg_order_value = total_spent / total_orders if total_orders > 0 else Decimal('0.00')
        
        return {
            'total_orders': total_orders,
            'total_spent': float(total_spent),
            'average_order_value': float(avg_order_value),
            'last_order_date': orders.last().created_at if orders.exists() else None
        }
    
    def _calculate_monthly_trends(self, user: User, months: int) -> List[Dict[str, Any]]:
        """Calculate monthly spending trends."""
        from .models import Order
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta
        
        end_date = timezone.now()
        start_date = end_date - relativedelta(months=months)
        
        orders = Order.objects.filter(
            user=user,
            status='completed',
            created_at__gte=start_date
        ).order_by('created_at')
        
        monthly_data = {}
        for order in orders:
            month_key = order.created_at.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {'total': Decimal('0.00'), 'count': 0}
            
            monthly_data[month_key]['total'] += order.total_amount
            monthly_data[month_key]['count'] += 1
        
        return [
            {
                'month': month,
                'total_spent': float(data['total']),
                'order_count': data['count']
            }
            for month, data in sorted(monthly_data.items())
        ]
    
    def _calculate_top_categories(self, user: User) -> List[Dict[str, Any]]:
        """Calculate top spending categories."""
        from .models import Order, OrderItem
        from django.db.models import Sum
        
        category_spending = (
            OrderItem.objects
            .filter(order__user=user, order__status='completed')
            .values('product__category__name')
            .annotate(total_spent=Sum('total_price'))
            .order_by('-total_spent')
        )
        
        return [
            {
                'category': item['product__category__name'],
                'total_spent': float(item['total_spent'])
            }
            for item in category_spending
        ]