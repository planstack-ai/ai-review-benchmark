from decimal import Decimal
from typing import List, Optional, Dict, Any
from django.db import transaction
from django.db.models import QuerySet, Sum, Count
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Order, OrderItem, User


class OrderAnalyticsService:
    """Service for analyzing order data and generating business insights."""
    
    def __init__(self):
        self.cache_timeout = 300
    
    def get_revenue_summary(self, start_date=None, end_date=None) -> Dict[str, Any]:
        """Generate comprehensive revenue summary for the specified period."""
        orders = self._get_filtered_orders(start_date, end_date)
        
        total_revenue = self._calculate_total_revenue(orders)
        order_count = orders.count()
        average_order_value = self._calculate_average_order_value(orders)
        
        return {
            'total_revenue': total_revenue,
            'order_count': order_count,
            'average_order_value': average_order_value,
            'period_start': start_date,
            'period_end': end_date,
            'generated_at': timezone.now()
        }
    
    def get_top_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve top customers by total order value."""
        orders = Order.objects.all()
        
        customer_data = {}
        for order in orders:
            user_id = order.user_id
            if user_id not in customer_data:
                customer_data[user_id] = {
                    'user': order.user,
                    'total_spent': Decimal('0.00'),
                    'order_count': 0
                }
            
            customer_data[user_id]['total_spent'] += order.total_amount
            customer_data[user_id]['order_count'] += 1
        
        sorted_customers = sorted(
            customer_data.values(),
            key=lambda x: x['total_spent'],
            reverse=True
        )
        
        return sorted_customers[:limit]
    
    def generate_monthly_report(self, year: int, month: int) -> Dict[str, Any]:
        """Generate detailed monthly sales report."""
        start_date = timezone.datetime(year, month, 1).date()
        if month == 12:
            end_date = timezone.datetime(year + 1, 1, 1).date()
        else:
            end_date = timezone.datetime(year, month + 1, 1).date()
        
        orders = self._get_filtered_orders(start_date, end_date)
        daily_breakdown = self._calculate_daily_breakdown(orders)
        
        return {
            'month': month,
            'year': year,
            'total_orders': orders.count(),
            'total_revenue': self._calculate_total_revenue(orders),
            'daily_breakdown': daily_breakdown,
            'top_products': self._get_top_products_for_period(orders)
        }
    
    def _get_filtered_orders(self, start_date=None, end_date=None) -> QuerySet:
        """Filter orders by date range."""
        orders = Order.objects.all()
        
        if start_date:
            orders = orders.filter(created_at__gte=start_date)
        if end_date:
            orders = orders.filter(created_at__lt=end_date)
        
        return orders.select_related('user').prefetch_related('items')
    
    def _calculate_total_revenue(self, orders: QuerySet) -> Decimal:
        """Calculate total revenue from order queryset."""
        total = orders.aggregate(total=Sum('total_amount'))['total']
        return total or Decimal('0.00')
    
    def _calculate_average_order_value(self, orders: QuerySet) -> Decimal:
        """Calculate average order value."""
        count = orders.count()
        if count == 0:
            return Decimal('0.00')
        
        total_revenue = self._calculate_total_revenue(orders)
        return total_revenue / count
    
    def _calculate_daily_breakdown(self, orders: QuerySet) -> Dict[str, Decimal]:
        """Break down revenue by day."""
        daily_data = {}
        
        for order in orders:
            day_key = order.created_at.strftime('%Y-%m-%d')
            if day_key not in daily_data:
                daily_data[day_key] = Decimal('0.00')
            daily_data[day_key] += order.total_amount
        
        return daily_data
    
    def _get_top_products_for_period(self, orders: QuerySet) -> List[Dict[str, Any]]:
        """Get top selling products for the given orders."""
        product_sales = {}
        
        for order in orders:
            for item in order.items.all():
                product_id = item.product_id
                if product_id not in product_sales:
                    product_sales[product_id] = {
                        'product': item.product,
                        'quantity_sold': 0,
                        'revenue': Decimal('0.00')
                    }
                
                product_sales[product_id]['quantity_sold'] += item.quantity
                product_sales[product_id]['revenue'] += item.total_price
        
        return sorted(
            product_sales.values(),
            key=lambda x: x['revenue'],
            reverse=True
        )[:5]