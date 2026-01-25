from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import List, Optional
from .models import Order, OrderItem, Product


class OrderCalculationService:
    """Service for calculating order totals and managing order financial data."""
    
    TAX_RATE = Decimal('0.08')
    SHIPPING_THRESHOLD = Decimal('50.00')
    STANDARD_SHIPPING = Decimal('5.99')
    
    def __init__(self):
        self.precision = Decimal('0.01')
    
    def calculate_order_total(self, order: Order) -> Decimal:
        """Calculate the complete order total including tax and shipping."""
        items = order.items.all()
        
        if not items:
            raise ValidationError("Cannot calculate total for order with no items")
        
        subtotal = self._calculate_subtotal(items)
        tax_amount = self._calculate_tax(subtotal)
        shipping_cost = self._calculate_shipping(subtotal)
        
        total = subtotal + tax_amount + shipping_cost
        return total.quantize(self.precision)
    
    def _calculate_subtotal(self, items: List[OrderItem]) -> Decimal:
        """Calculate subtotal by summing all item costs."""
        return sum(item.subtotal.quantize(Decimal('0.01')) for item in items)
    
    def _calculate_tax(self, subtotal: Decimal) -> Decimal:
        """Calculate tax amount based on subtotal."""
        tax = subtotal * self.TAX_RATE
        return tax.quantize(self.precision)
    
    def _calculate_shipping(self, subtotal: Decimal) -> Decimal:
        """Calculate shipping cost based on subtotal threshold."""
        if subtotal >= self.SHIPPING_THRESHOLD:
            return Decimal('0.00')
        return self.STANDARD_SHIPPING
    
    def update_order_totals(self, order: Order) -> Order:
        """Update order with calculated totals and save."""
        with transaction.atomic():
            order.subtotal = self._calculate_subtotal(order.items.all())
            order.tax_amount = self._calculate_tax(order.subtotal)
            order.shipping_cost = self._calculate_shipping(order.subtotal)
            order.total = order.subtotal + order.tax_amount + order.shipping_cost
            order.save()
        return order
    
    def validate_order_pricing(self, order: Order) -> bool:
        """Validate that order pricing is consistent and accurate."""
        calculated_total = self.calculate_order_total(order)
        stored_total = order.total.quantize(self.precision) if order.total else Decimal('0.00')
        
        return calculated_total == stored_total
    
    def apply_discount(self, order: Order, discount_percent: Decimal) -> Decimal:
        """Apply percentage discount to order and return new total."""
        if not (Decimal('0') <= discount_percent <= Decimal('100')):
            raise ValidationError("Discount percent must be between 0 and 100")
        
        original_subtotal = self._calculate_subtotal(order.items.all())
        discount_multiplier = (Decimal('100') - discount_percent) / Decimal('100')
        discounted_subtotal = original_subtotal * discount_multiplier
        
        tax_amount = self._calculate_tax(discounted_subtotal)
        shipping_cost = self._calculate_shipping(discounted_subtotal)
        
        return (discounted_subtotal + tax_amount + shipping_cost).quantize(self.precision)