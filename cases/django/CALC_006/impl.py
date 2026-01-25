from decimal import Decimal
from typing import Dict, List, Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

from .models import Order, OrderItem, ShippingMethod, Product


class OrderShippingService:
    """Service class for handling order shipping calculations and processing."""
    
    FREE_SHIPPING_THRESHOLD = Decimal('5000.00')
    DEFAULT_SHIPPING_FEE = Decimal('500.00')
    EXPRESS_SHIPPING_FEE = Decimal('1200.00')
    
    def __init__(self):
        self.shipping_methods = self._load_shipping_methods()
    
    def calculate_shipping_cost(self, order: Order, shipping_method: str = 'standard') -> Decimal:
        """Calculate shipping cost for an order based on total amount and shipping method."""
        if not order or not order.items.exists():
            raise ValidationError("Order must have items to calculate shipping")
        
        order_total = self._calculate_order_total(order)
        base_shipping_fee = self._get_base_shipping_fee(shipping_method)
        
        if self._qualifies_for_free_shipping(order_total):
            return Decimal('0.00')
        
        return self._apply_shipping_adjustments(base_shipping_fee, order)
    
    def process_shipping_for_order(self, order_id: int, shipping_method: str = 'standard') -> Dict:
        """Process shipping calculation and update order with shipping details."""
        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=order_id)
                
                if order.status != 'pending':
                    raise ValidationError("Can only process shipping for pending orders")
                
                shipping_cost = self.calculate_shipping_cost(order, shipping_method)
                
                order.shipping_method = shipping_method
                order.shipping_cost = shipping_cost
                order.updated_at = timezone.now()
                order.save()
                
                return {
                    'order_id': order.id,
                    'shipping_cost': shipping_cost,
                    'shipping_method': shipping_method,
                    'free_shipping_applied': shipping_cost == Decimal('0.00'),
                    'order_total': self._calculate_order_total(order)
                }
                
        except Order.DoesNotExist:
            raise ValidationError(f"Order with ID {order_id} not found")
    
    def get_shipping_options(self, order: Order) -> List[Dict]:
        """Get available shipping options with costs for an order."""
        order_total = self._calculate_order_total(order)
        options = []
        
        for method_code, method_info in self.shipping_methods.items():
            base_cost = method_info['base_cost']
            
            if self._qualifies_for_free_shipping(order_total) and method_code == 'standard':
                final_cost = Decimal('0.00')
            else:
                final_cost = self._apply_shipping_adjustments(base_cost, order)
            
            options.append({
                'code': method_code,
                'name': method_info['name'],
                'cost': final_cost,
                'estimated_days': method_info['estimated_days']
            })
        
        return options
    
    def _calculate_order_total(self, order: Order) -> Decimal:
        """Calculate the total value of order items."""
        total = Decimal('0.00')
        for item in order.items.select_related('product'):
            item_total = item.quantity * item.unit_price
            total += item_total
        return total
    
    def _qualifies_for_free_shipping(self, order_total: Decimal) -> bool:
        """Check if order qualifies for free shipping based on total amount."""
        return order_total > self.FREE_SHIPPING_THRESHOLD
    
    def _get_base_shipping_fee(self, shipping_method: str) -> Decimal:
        """Get base shipping fee for the specified method."""
        method_info = self.shipping_methods.get(shipping_method)
        if not method_info:
            return self.DEFAULT_SHIPPING_FEE
        return method_info['base_cost']
    
    def _apply_shipping_adjustments(self, base_fee: Decimal, order: Order) -> Decimal:
        """Apply any additional shipping adjustments based on order characteristics."""
        adjusted_fee = base_fee
        
        if self._has_oversized_items(order):
            adjusted_fee += Decimal('300.00')
        
        if self._has_fragile_items(order):
            adjusted_fee += Decimal('200.00')
        
        return adjusted_fee
    
    def _has_oversized_items(self, order: Order) -> bool:
        """Check if order contains oversized items."""
        return order.items.filter(product__is_oversized=True).exists()
    
    def _has_fragile_items(self, order: Order) -> bool:
        """Check if order contains fragile items."""
        return order.items.filter(product__is_fragile=True).exists()
    
    def _load_shipping_methods(self) -> Dict:
        """Load available shipping methods configuration."""
        return {
            'standard': {
                'name': 'Standard Shipping',
                'base_cost': self.DEFAULT_SHIPPING_FEE,
                'estimated_days': 5
            },
            'express': {
                'name': 'Express Shipping',
                'base_cost': self.EXPRESS_SHIPPING_FEE,
                'estimated_days': 2
            }
        }