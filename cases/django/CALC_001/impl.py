from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import Optional, Dict, Any
from django.contrib.auth.models import User
from myapp.models import Order, OrderItem, Membership


class OrderDiscountService:
    """Service for handling order discount calculations and applications."""
    
    def __init__(self):
        self.member_discount_rate = Decimal('0.10')
        self.minimum_order_amount = Decimal('50.00')
    
    def calculate_order_total(self, order: Order, user: User) -> Dict[str, Any]:
        """Calculate the final order total with applicable discounts."""
        subtotal = self._calculate_subtotal(order)
        discount_amount = Decimal('0.00')
        final_total = subtotal
        
        if self._is_eligible_for_member_discount(user, subtotal):
            discount_amount = self._calculate_member_discount(subtotal)
            final_total = subtotal - discount_amount
        
        return {
            'subtotal': subtotal,
            'discount_amount': discount_amount,
            'final_total': final_total,
            'discount_applied': discount_amount > 0
        }
    
    @transaction.atomic
    def apply_discount_to_order(self, order: Order, user: User) -> Order:
        """Apply member discount to an order and save the changes."""
        if not self._validate_order_for_discount(order):
            raise ValidationError("Order is not valid for discount application")
        
        calculation_result = self.calculate_order_total(order, user)
        
        order.subtotal = calculation_result['subtotal']
        order.discount_amount = calculation_result['discount_amount']
        order.total = calculation_result['final_total']
        order.save()
        
        return order
    
    def _calculate_subtotal(self, order: Order) -> Decimal:
        """Calculate the subtotal from all order items."""
        subtotal = Decimal('0.00')
        for item in order.items.all():
            item_total = item.quantity * item.unit_price
            subtotal += item_total
        return subtotal
    
    def _is_eligible_for_member_discount(self, user: User, subtotal: Decimal) -> bool:
        """Check if user is eligible for member discount."""
        if not user.is_authenticated:
            return False
        
        try:
            membership = Membership.objects.get(user=user, is_active=True)
            return membership.is_valid() and subtotal >= self.minimum_order_amount
        except Membership.DoesNotExist:
            return False
    
    def _calculate_member_discount(self, total: Decimal) -> Decimal:
        """Calculate the discount amount for members."""
        return total * self.member_discount_rate
    
    def _validate_order_for_discount(self, order: Order) -> bool:
        """Validate that the order can have discounts applied."""
        if not order or not order.items.exists():
            return False
        
        if order.status in ['cancelled', 'refunded']:
            return False
        
        return True
    
    def get_discount_preview(self, user: User, cart_items: list) -> Optional[Dict[str, Any]]:
        """Preview discount calculation without applying to an order."""
        if not cart_items:
            return None
        
        estimated_total = sum(
            Decimal(str(item['quantity'])) * Decimal(str(item['price'])) 
            for item in cart_items
        )
        
        if self._is_member_eligible_for_preview(user, estimated_total):
            discount_amount = self._calculate_member_discount(estimated_total)
            return {
                'estimated_total': estimated_total,
                'discount_amount': discount_amount,
                'final_total': estimated_total - discount_amount,
                'savings_percentage': (discount_amount / estimated_total * 100).quantize(Decimal('0.01'))
            }
        
        return {
            'estimated_total': estimated_total,
            'discount_amount': Decimal('0.00'),
            'final_total': estimated_total,
            'savings_percentage': Decimal('0.00')
        }
    
    def _is_member_eligible_for_preview(self, user: User, total: Decimal) -> bool:
        """Check member eligibility for discount preview."""
        return (user.is_authenticated and 
                total >= self.minimum_order_amount and
                hasattr(user, 'membership') and 
                user.membership.is_active)