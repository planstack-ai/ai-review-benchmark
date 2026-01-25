from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class OrderItem:
    product_id: int
    unit_price: float
    quantity: int
    discount_percent: float = 0.0


class BulkOrderCalculationService:
    """Service for calculating totals and processing bulk orders."""
    
    def __init__(self):
        self.tax_rate = Decimal('0.08')
        self.bulk_discount_threshold = 100
        self.bulk_discount_rate = Decimal('0.05')
    
    def calculate_order_total(self, order_items: List[OrderItem]) -> Dict[str, Any]:
        """Calculate the total cost for a bulk order including taxes and discounts."""
        if not order_items:
            raise ValidationError("Order must contain at least one item")
        
        subtotal = self._calculate_subtotal(order_items)
        bulk_discount = self._calculate_bulk_discount(subtotal, order_items)
        tax_amount = self._calculate_tax(subtotal - bulk_discount)
        
        return {
            'subtotal': subtotal,
            'bulk_discount': bulk_discount,
            'tax_amount': tax_amount,
            'total': subtotal - bulk_discount + tax_amount,
            'item_count': sum(item.quantity for item in order_items)
        }
    
    def _calculate_subtotal(self, order_items: List[OrderItem]) -> Decimal:
        """Calculate subtotal for all items before discounts and taxes."""
        subtotal = Decimal('0')
        
        for item in order_items:
            self._validate_order_item(item)
            item_total = self._calculate_item_total(item)
            subtotal += item_total
        
        return subtotal
    
    def _calculate_item_total(self, item: OrderItem) -> Decimal:
        """Calculate total for a single order item including item-level discount."""
        base_total = item.unit_price * item.quantity
        discount_amount = base_total * (item.discount_percent / 100)
        return Decimal(str(base_total - discount_amount))
    
    def _calculate_bulk_discount(self, subtotal: Decimal, order_items: List[OrderItem]) -> Decimal:
        """Apply bulk discount if order qualifies."""
        total_quantity = sum(item.quantity for item in order_items)
        
        if total_quantity >= self.bulk_discount_threshold:
            return subtotal * self.bulk_discount_rate
        
        return Decimal('0')
    
    def _calculate_tax(self, taxable_amount: Decimal) -> Decimal:
        """Calculate tax on the taxable amount."""
        return taxable_amount * self.tax_rate
    
    def _validate_order_item(self, item: OrderItem) -> None:
        """Validate individual order item parameters."""
        if item.quantity <= 0:
            raise ValidationError(f"Quantity must be positive for product {item.product_id}")
        
        if item.unit_price < 0:
            raise ValidationError(f"Unit price cannot be negative for product {item.product_id}")
        
        if not (0 <= item.discount_percent <= 100):
            raise ValidationError(f"Discount percent must be between 0 and 100 for product {item.product_id}")
    
    @transaction.atomic
    def process_bulk_order(self, order_items: List[OrderItem], customer_id: int) -> Dict[str, Any]:
        """Process a complete bulk order with validation and calculation."""
        calculation_result = self.calculate_order_total(order_items)
        
        order_data = {
            'customer_id': customer_id,
            'status': 'pending',
            **calculation_result
        }
        
        return order_data