from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import Dict, List, Optional
from .models import Order, OrderItem, Discount


class OrderValidationService:
    """Service for validating order requirements and business rules."""
    
    MINIMUM_ORDER_AMOUNT = Decimal('1000.00')
    
    def __init__(self):
        self.validation_errors = []
    
    def validate_order(self, order: Order) -> Dict[str, any]:
        """
        Validates an order against all business rules.
        Returns validation result with status and details.
        """
        self.validation_errors.clear()
        
        subtotal = self._calculate_subtotal(order)
        applicable_discounts = self._get_applicable_discounts(order)
        discount_amount = self._calculate_discount_amount(subtotal, applicable_discounts)
        
        validation_result = {
            'is_valid': True,
            'subtotal': subtotal,
            'discount_amount': discount_amount,
            'final_amount': subtotal - discount_amount,
            'errors': []
        }
        
        if not self._validate_minimum_order_amount(subtotal):
            validation_result['is_valid'] = False
            validation_result['errors'].append(
                f'Order must be at least {self.MINIMUM_ORDER_AMOUNT} yen'
            )
        
        if not self._validate_order_items(order):
            validation_result['is_valid'] = False
            validation_result['errors'].extend(self.validation_errors)
        
        return validation_result
    
    def _calculate_subtotal(self, order: Order) -> Decimal:
        """Calculate the subtotal before any discounts are applied."""
        subtotal = Decimal('0.00')
        
        for item in order.items.all():
            item_total = item.quantity * item.unit_price
            subtotal += item_total
        
        return subtotal
    
    def _get_applicable_discounts(self, order: Order) -> List[Discount]:
        """Retrieve all discounts that can be applied to this order."""
        applicable_discounts = []
        
        for discount in Discount.objects.filter(is_active=True):
            if self._is_discount_applicable(order, discount):
                applicable_discounts.append(discount)
        
        return applicable_discounts
    
    def _calculate_discount_amount(self, subtotal: Decimal, discounts: List[Discount]) -> Decimal:
        """Calculate total discount amount from applicable discounts."""
        total_discount = Decimal('0.00')
        
        for discount in discounts:
            if discount.discount_type == 'percentage':
                discount_value = subtotal * (discount.value / Decimal('100'))
            else:
                discount_value = discount.value
            
            total_discount += discount_value
        
        return min(total_discount, subtotal)
    
    def _validate_minimum_order_amount(self, subtotal: Decimal) -> bool:
        """Check if order meets minimum amount requirement."""
        return subtotal >= self.MINIMUM_ORDER_AMOUNT
    
    def _validate_order_items(self, order: Order) -> bool:
        """Validate individual order items for business rules."""
        if not order.items.exists():
            self.validation_errors.append('Order must contain at least one item')
            return False
        
        for item in order.items.all():
            if item.quantity <= 0:
                self.validation_errors.append(f'Invalid quantity for item {item.product.name}')
                return False
            
            if item.unit_price <= 0:
                self.validation_errors.append(f'Invalid price for item {item.product.name}')
                return False
        
        return True
    
    def _is_discount_applicable(self, order: Order, discount: Discount) -> bool:
        """Check if a specific discount can be applied to the order."""
        if discount.minimum_order_amount and order.subtotal < discount.minimum_order_amount:
            return False
        
        if discount.customer_type and order.customer.customer_type != discount.customer_type:
            return False
        
        return True