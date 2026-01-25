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
        return sum(item.subtotal.quantize(self.precision) for item in items)
    
    def _calculate_tax(self, subtotal: Decimal) -> Decimal:
        """Calculate tax amount based on subtotal."""
        tax = subtotal * self.TAX_RATE
        return tax.quantize(self.precision)
    
    def _calculate_shipping(self, subtotal: Decimal) -> Decimal:
        """Calculate shipping cost based on subtotal threshold."""
        if subtotal >= self.SHIPPING_THRESHOLD:
            return Decimal('0.00')
        return self.STANDARD_SHIPPING
    
    def update_item_subtotal(self, item: OrderItem) -> None:
        """Update individual item subtotal based on quantity and price."""
        if item.quantity <= 0:
            raise ValidationError("Item quantity must be positive")
        
        base_cost = item.product.price * item.quantity
        discount_amount = self._calculate_item_discount(item)
        item.subtotal = base_cost - discount_amount
        item.save()
    
    def _calculate_item_discount(self, item: OrderItem) -> Decimal:
        """Calculate discount for individual item based on quantity."""
        if item.quantity >= 10:
            return item.product.price * item.quantity * Decimal('0.05')
        elif item.quantity >= 5:
            return item.product.price * item.quantity * Decimal('0.02')
        return Decimal('0.00')
    
    @transaction.atomic
    def recalculate_order(self, order: Order) -> Order:
        """Recalculate entire order including all items and totals."""
        for item in order.items.all():
            self.update_item_subtotal(item)
        
        order.total = self.calculate_order_total(order)
        order.save()
        return order
    
    def validate_order_pricing(self, order: Order) -> bool:
        """Validate that order pricing is consistent and accurate."""
        calculated_total = self.calculate_order_total(order)
        return abs(order.total - calculated_total) < Decimal('0.01')