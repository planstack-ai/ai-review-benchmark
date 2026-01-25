from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import Optional, Dict, Any
from .models import Order, Coupon, CouponUsage


class CouponService:
    """Service class for handling coupon operations and discount calculations."""
    
    def __init__(self):
        self.max_discount_percentage = Decimal('50.00')
        self.min_order_amount = Decimal('10.00')
    
    def apply_coupon_to_order(self, order: Order, coupon_code: str) -> Dict[str, Any]:
        """Apply a coupon to an order and calculate the discount."""
        try:
            coupon = self._get_valid_coupon(coupon_code)
            self._validate_coupon_eligibility(order, coupon)
            
            discount_amount = self._calculate_discount(order, coupon)
            
            with transaction.atomic():
                self._apply_coupon(order, coupon, discount_amount)
                self._create_coupon_usage_record(order, coupon)
            
            return {
                'success': True,
                'discount_amount': discount_amount,
                'final_total': order.total_amount - discount_amount,
                'coupon_code': coupon_code
            }
            
        except ValidationError as e:
            return {
                'success': False,
                'error': str(e),
                'discount_amount': Decimal('0.00')
            }
    
    def _get_valid_coupon(self, coupon_code: str) -> Coupon:
        """Retrieve and validate coupon exists and is active."""
        try:
            coupon = Coupon.objects.get(code=coupon_code.upper(), is_active=True)
        except Coupon.DoesNotExist:
            raise ValidationError(f"Invalid or inactive coupon code: {coupon_code}")
        
        if not coupon.is_valid():
            raise ValidationError("Coupon has expired or reached usage limit")
        
        return coupon
    
    def _validate_coupon_eligibility(self, order: Order, coupon: Coupon) -> None:
        """Validate if the coupon can be applied to this order."""
        if order.total_amount < coupon.minimum_order_amount:
            raise ValidationError(
                f"Order amount must be at least ${coupon.minimum_order_amount}"
            )
        
        if coupon.user_specific and coupon.allowed_user != order.user:
            raise ValidationError("This coupon is not valid for your account")
        
        existing_usage = CouponUsage.objects.filter(
            user=order.user,
            coupon=coupon
        ).count()
        
        if existing_usage >= coupon.max_uses_per_user:
            raise ValidationError("You have already used this coupon the maximum number of times")
    
    def _calculate_discount(self, order: Order, coupon: Coupon) -> Decimal:
        """Calculate the discount amount based on coupon type."""
        if coupon.discount_type == 'percentage':
            discount = (order.total_amount * coupon.discount_value) / Decimal('100')
            if coupon.max_discount_amount:
                discount = min(discount, coupon.max_discount_amount)
        else:
            discount = min(coupon.discount_value, order.total_amount)
        
        return discount.quantize(Decimal('0.01'))
    
    def _apply_coupon(self, order: Order, coupon: Coupon, discount_amount: Decimal) -> None:
        """Apply the coupon discount to the order."""
        order.applied_coupons.add(coupon)
        order.discount_amount += discount_amount
        order.total_amount -= discount_amount
        order.save()
    
    def _create_coupon_usage_record(self, order: Order, coupon: Coupon) -> None:
        """Create a record of coupon usage for tracking purposes."""
        CouponUsage.objects.create(
            user=order.user,
            coupon=coupon,
            order=order,
            discount_applied=order.discount_amount
        )
    
    def remove_coupon_from_order(self, order: Order, coupon_code: str) -> bool:
        """Remove a previously applied coupon from an order."""
        try:
            coupon = Coupon.objects.get(code=coupon_code.upper())
            if coupon in order.applied_coupons.all():
                with transaction.atomic():
                    order.applied_coupons.remove(coupon)
                    self._recalculate_order_total(order)
                return True
        except Coupon.DoesNotExist:
            pass
        return False
    
    def _recalculate_order_total(self, order: Order) -> None:
        """Recalculate order total after coupon removal."""
        order.discount_amount = Decimal('0.00')
        order.total_amount = order.subtotal_amount
        
        for coupon in order.applied_coupons.all():
            discount = self._calculate_discount(order, coupon)
            order.discount_amount += discount
            order.total_amount -= discount
        
        order.save()