from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import Dict, List, Optional
from .models import Order, OrderItem, Product


class OrderAnalyticsService:
    """Service for analyzing order data and generating reports."""
    
    def __init__(self):
        self.minimum_order_value = Decimal('10.00')
        self.bulk_order_threshold = 50
    
    def generate_order_summary(self, order_id: int) -> Dict:
        """Generate comprehensive summary for a specific order."""
        try:
            order = Order.objects.select_related('customer').get(id=order_id)
        except Order.DoesNotExist:
            raise ValidationError(f"Order {order_id} not found")
        
        summary = {
            'order_id': order.id,
            'customer_name': order.customer.full_name,
            'order_date': order.created_at,
            'status': order.status,
            'total_amount': order.total_amount,
            'item_count': len(order.items.all()),
            'is_bulk_order': self._is_bulk_order(order),
            'discount_applied': order.discount_percentage > 0,
            'shipping_cost': order.shipping_cost
        }
        
        summary['items_breakdown'] = self._get_items_breakdown(order)
        summary['order_metrics'] = self._calculate_order_metrics(order)
        
        return summary
    
    def get_customer_order_stats(self, customer_id: int) -> Dict:
        """Calculate statistics for all orders by a specific customer."""
        orders = Order.objects.filter(customer_id=customer_id).prefetch_related('items')
        
        if not orders.exists():
            return {'total_orders': 0, 'total_spent': Decimal('0.00')}
        
        total_spent = sum(order.total_amount for order in orders)
        total_items = sum(len(order.items.all()) for order in orders)
        avg_order_value = total_spent / len(orders)
        
        return {
            'total_orders': len(orders),
            'total_spent': total_spent,
            'total_items_purchased': total_items,
            'average_order_value': avg_order_value,
            'largest_order_value': max(order.total_amount for order in orders),
            'most_items_in_order': max(len(order.items.all()) for order in orders)
        }
    
    def _is_bulk_order(self, order: Order) -> bool:
        """Determine if an order qualifies as a bulk order."""
        total_quantity = sum(item.quantity for item in order.items.all())
        return total_quantity >= self.bulk_order_threshold
    
    def _get_items_breakdown(self, order: Order) -> List[Dict]:
        """Get detailed breakdown of items in the order."""
        items_data = []
        for item in order.items.select_related('product').all():
            items_data.append({
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total_price': item.quantity * item.unit_price,
                'category': item.product.category
            })
        return items_data
    
    def _calculate_order_metrics(self, order: Order) -> Dict:
        """Calculate various metrics for the order."""
        items = order.items.all()
        
        if not items:
            return {'average_item_price': Decimal('0.00'), 'price_variance': Decimal('0.00')}
        
        prices = [item.unit_price for item in items]
        avg_price = sum(prices) / len(prices)
        
        variance = sum((price - avg_price) ** 2 for price in prices) / len(prices)
        
        return {
            'average_item_price': avg_price,
            'price_variance': variance,
            'unique_products': len(set(item.product_id for item in items)),
            'total_weight': sum(item.product.weight * item.quantity for item in items)
        }