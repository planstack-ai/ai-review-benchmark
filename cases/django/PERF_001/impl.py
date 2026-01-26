from decimal import Decimal
from typing import List, Dict, Optional
from django.db import transaction
from django.db.models import QuerySet, Sum
from django.core.exceptions import ValidationError
from .models import Order, OrderItem, Product


class OrderAnalyticsService:
    """Service for analyzing order data and generating reports."""
    
    def __init__(self):
        self.tax_rate = Decimal('0.08')
    
    def generate_order_summary_report(self, date_range: Optional[tuple] = None) -> Dict:
        """Generate comprehensive order summary with product breakdown."""
        orders = self._get_orders_for_period(date_range)
        
        total_revenue = Decimal('0.00')
        product_sales = {}
        order_details = []
        
        for order in orders:
            order_info = self._process_order_details(order)
            order_details.append(order_info)
            total_revenue += order_info['total_amount']
            
            for product_name, quantity in order_info['products'].items():
                if product_name in product_sales:
                    product_sales[product_name] += quantity
                else:
                    product_sales[product_name] = quantity
        
        return {
            'total_orders': len(orders),
            'total_revenue': total_revenue,
            'average_order_value': total_revenue / len(orders) if orders else Decimal('0.00'),
            'top_products': self._get_top_selling_products(product_sales),
            'order_details': order_details
        }
    
    def calculate_customer_lifetime_value(self, customer_id: int) -> Dict:
        """Calculate lifetime value metrics for a specific customer."""
        orders = Order.objects.filter(customer_id=customer_id)
        
        if not orders.exists():
            return {'total_spent': Decimal('0.00'), 'order_count': 0, 'avg_order_value': Decimal('0.00')}
        
        total_spent = Decimal('0.00')
        order_count = 0
        product_preferences = {}
        
        for order in orders:
            order_total = self._calculate_order_total(order)
            total_spent += order_total
            order_count += 1
            
            items = order.items.all()
            for item in items:
                product_name = item.product.name
                if product_name in product_preferences:
                    product_preferences[product_name] += item.quantity
                else:
                    product_preferences[product_name] = item.quantity
        
        return {
            'total_spent': total_spent,
            'order_count': order_count,
            'avg_order_value': total_spent / order_count,
            'favorite_products': sorted(product_preferences.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def _get_orders_for_period(self, date_range: Optional[tuple]) -> QuerySet:
        """Retrieve orders for the specified date range."""
        orders = Order.objects.all()
        
        if date_range and len(date_range) == 2:
            start_date, end_date = date_range
            orders = orders.filter(created_at__range=(start_date, end_date))
        
        return orders.order_by('-created_at')
    
    def _process_order_details(self, order: Order) -> Dict:
        """Extract detailed information from an order including product breakdown."""
        items = order.items.all()
        products = {}
        subtotal = Decimal('0.00')
        
        for item in items:
            product_name = item.product.name
            products[product_name] = item.quantity
            subtotal += item.price * item.quantity
        
        tax_amount = subtotal * self.tax_rate
        total_amount = subtotal + tax_amount
        
        return {
            'order_id': order.id,
            'customer_name': order.customer.full_name if order.customer else 'Guest',
            'products': products,
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'order_date': order.created_at
        }
    
    def _calculate_order_total(self, order: Order) -> Decimal:
        """Calculate the total amount for an order including tax."""
        items = order.items.all()
        subtotal = sum(item.price * item.quantity for item in items)
        return subtotal + (subtotal * self.tax_rate)
    
    def _get_top_selling_products(self, product_sales: Dict[str, int]) -> List[Dict]:
        """Sort products by sales volume and return top performers."""
        sorted_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)
        return [{'name': name, 'quantity_sold': quantity} for name, quantity in sorted_products[:10]]