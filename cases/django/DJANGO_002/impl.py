from typing import List, Optional, Dict, Any
from decimal import Decimal
from django.db import transaction
from django.db.models import QuerySet, Sum, Count
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime

from .models import Order, OrderItem, Product, Customer


class OrderAnalyticsService:
    """Service for analyzing order data and generating reports."""
    
    def __init__(self):
        self.cache_timeout = 300
    
    def get_order_summary_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive order summary report for date range."""
        orders = self._get_orders_with_items(start_date, end_date)
        
        total_revenue = Decimal('0.00')
        total_orders = orders.count()
        item_counts = {}
        
        for order in orders:
            order_total = self._calculate_order_total(order)
            total_revenue += order_total
            
            for item in order.items.all():
                product_name = item.product.name
                if product_name in item_counts:
                    item_counts[product_name] += item.quantity
                else:
                    item_counts[product_name] = item.quantity
        
        return {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'average_order_value': total_revenue / total_orders if total_orders > 0 else Decimal('0.00'),
            'top_products': self._get_top_products(item_counts),
            'period': f"{start_date.date()} to {end_date.date()}"
        }
    
    def get_customer_order_history(self, customer_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve detailed order history for a specific customer."""
        orders = self._get_customer_orders_with_details(customer_id, limit)
        
        history = []
        for order in orders:
            order_data = {
                'order_id': order.id,
                'order_date': order.created_at,
                'status': order.status,
                'total_amount': self._calculate_order_total(order),
                'items': []
            }
            
            for item in order.items.all():
                item_data = {
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'subtotal': item.quantity * item.unit_price
                }
                order_data['items'].append(item_data)
            
            history.append(order_data)
        
        return history
    
    def _get_orders_with_items(self, start_date: datetime, end_date: datetime) -> QuerySet:
        """Retrieve orders with their items for the specified date range."""
        return Order.objects.select_related('items').filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).order_by('-created_at')
    
    def _get_customer_orders_with_details(self, customer_id: int, limit: int) -> QuerySet:
        """Get customer orders with all related data efficiently loaded."""
        return Order.objects.select_related('items').filter(
            customer_id=customer_id
        ).order_by('-created_at')[:limit]
    
    def _calculate_order_total(self, order) -> Decimal:
        """Calculate the total amount for an order."""
        total = Decimal('0.00')
        for item in order.items.all():
            total += item.quantity * item.unit_price
        return total
    
    def _get_top_products(self, item_counts: Dict[str, int], limit: int = 10) -> List[Dict[str, Any]]:
        """Get top selling products from item counts."""
        sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
        return [
            {'product_name': name, 'quantity_sold': count}
            for name, count in sorted_items[:limit]
        ]