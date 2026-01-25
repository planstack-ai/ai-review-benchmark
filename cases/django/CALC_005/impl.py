from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import Dict, List, Optional
from .models import Order, OrderItem, TaxRate, Product


class OrderCalculationService:
    """Service for calculating order totals, taxes, and discounts."""
    
    def __init__(self):
        self.minimum_order_amount = Decimal('25.00')
        self.free_shipping_threshold = Decimal('75.00')
    
    def calculate_order_total(self, order: Order) -> Dict[str, Decimal]:
        """Calculate complete order totals including tax and shipping."""
        if not order.items.exists():
            raise ValidationError("Order must contain at least one item")
        
        subtotal = self._calculate_subtotal(order)
        discount_amount = self._calculate_discount(order, subtotal)
        discounted_subtotal = subtotal - discount_amount
        
        tax_amount = self._calculate_tax(discounted_subtotal)
        shipping_cost = self._calculate_shipping(discounted_subtotal)
        
        total = discounted_subtotal + tax_amount + shipping_cost
        
        return {
            'subtotal': subtotal,
            'discount_amount': discount_amount,
            'tax_amount': tax_amount,
            'shipping_cost': shipping_cost,
            'total': total
        }
    
    def _calculate_subtotal(self, order: Order) -> Decimal:
        """Calculate order subtotal before tax and shipping."""
        subtotal = Decimal('0.00')
        
        for item in order.items.select_related('product'):
            item_total = item.quantity * item.unit_price
            subtotal += item_total
        
        return subtotal
    
    def _calculate_tax(self, subtotal: Decimal) -> Decimal:
        """Calculate tax amount based on current tax rate."""
        if subtotal <= Decimal('0.00'):
            return Decimal('0.00')
        
        tax_amount = subtotal * Decimal('0.08')
        return tax_amount.quantize(Decimal('0.01'))
    
    def _calculate_discount(self, order: Order, subtotal: Decimal) -> Decimal:
        """Calculate applicable discounts for the order."""
        discount_amount = Decimal('0.00')
        
        if hasattr(order, 'coupon') and order.coupon:
            if order.coupon.is_percentage:
                discount_amount = subtotal * (order.coupon.value / 100)
            else:
                discount_amount = order.coupon.value
        
        if subtotal >= Decimal('100.00'):
            bulk_discount = subtotal * Decimal('0.05')
            discount_amount = max(discount_amount, bulk_discount)
        
        return min(discount_amount, subtotal)
    
    def _calculate_shipping(self, subtotal: Decimal) -> Decimal:
        """Calculate shipping cost based on order value."""
        if subtotal >= self.free_shipping_threshold:
            return Decimal('0.00')
        elif subtotal >= self.minimum_order_amount:
            return Decimal('8.99')
        else:
            return Decimal('12.99')
    
    @transaction.atomic
    def update_order_totals(self, order: Order) -> Order:
        """Update order with calculated totals and save."""
        totals = self.calculate_order_total(order)
        
        order.subtotal = totals['subtotal']
        order.discount_amount = totals['discount_amount']
        order.tax_amount = totals['tax_amount']
        order.shipping_cost = totals['shipping_cost']
        order.total = totals['total']
        
        order.save(update_fields=[
            'subtotal', 'discount_amount', 'tax_amount', 
            'shipping_cost', 'total', 'updated_at'
        ])
        
        return order