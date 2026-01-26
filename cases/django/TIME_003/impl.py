from decimal import Decimal
from typing import Optional, Dict, Any
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from myapp.models import Coupon, Order, CouponUsage


class CouponService:
    """Service class for handling coupon operations and validations."""
    
    def __init__(self):
        self.max_usage_per_user = 5
        self.min_order_amount = Decimal('10.00')
    
    def validate_coupon(self, coupon_code: str, user_id: int, order_amount: Decimal) -> Dict[str, Any]:
        """
        Validates a coupon for use by a specific user and order.
        
        Returns a dictionary with validation results and coupon details.
        """
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
        except Coupon.DoesNotExist:
            return {'valid': False, 'error': 'Invalid coupon code'}
        
        if not self._is_coupon_valid_for_date(coupon):
            return {'valid': False, 'error': 'Coupon has expired'}
        
        if not self._check_usage_limits(coupon, user_id):
            return {'valid': False, 'error': 'Coupon usage limit exceeded'}
        
        if not self._meets_minimum_order_amount(coupon, order_amount):
            return {'valid': False, 'error': f'Minimum order amount of ${coupon.minimum_amount} required'}
        
        discount_amount = self._calculate_discount(coupon, order_amount)
        
        return {
            'valid': True,
            'coupon': coupon,
            'discount_amount': discount_amount,
            'final_amount': order_amount - discount_amount
        }
    
    def _is_coupon_valid_for_date(self, coupon: Coupon) -> bool:
        """Check if coupon is within valid date range."""
        current_time = timezone.now()
        
        if coupon.starts_at and current_time < coupon.starts_at:
            return False
        
        if coupon.expires_at and current_time < coupon.expires_at:
            return False
        
        return True
    
    def _check_usage_limits(self, coupon: Coupon, user_id: int) -> bool:
        """Verify coupon usage limits haven't been exceeded."""
        if coupon.max_uses and coupon.times_used >= coupon.max_uses:
            return False
        
        if coupon.max_uses_per_user:
            user_usage_count = CouponUsage.objects.filter(
                coupon=coupon,
                user_id=user_id
            ).count()
            
            if user_usage_count >= coupon.max_uses_per_user:
                return False
        
        return True
    
    def _meets_minimum_order_amount(self, coupon: Coupon, order_amount: Decimal) -> bool:
        """Check if order meets minimum amount requirement."""
        if coupon.minimum_amount and order_amount < coupon.minimum_amount:
            return False
        return True
    
    def _calculate_discount(self, coupon: Coupon, order_amount: Decimal) -> Decimal:
        """Calculate the discount amount based on coupon type."""
        if coupon.discount_type == 'percentage':
            discount = order_amount * (coupon.discount_value / Decimal('100'))
            if coupon.max_discount_amount:
                discount = min(discount, coupon.max_discount_amount)
            return discount
        elif coupon.discount_type == 'fixed':
            return min(coupon.discount_value, order_amount)
        return Decimal('0.00')
    
    @transaction.atomic
    def apply_coupon(self, coupon_code: str, order: Order) -> bool:
        """Apply a validated coupon to an order."""
        validation_result = self.validate_coupon(
            coupon_code, 
            order.user_id, 
            order.total_amount
        )
        
        if not validation_result['valid']:
            raise ValidationError(validation_result['error'])
        
        coupon = validation_result['coupon']
        discount_amount = validation_result['discount_amount']
        
        order.coupon = coupon
        order.discount_amount = discount_amount
        order.final_amount = validation_result['final_amount']
        order.save()
        
        coupon.times_used += 1
        coupon.save()
        
        CouponUsage.objects.create(
            coupon=coupon,
            user_id=order.user_id,
            order=order,
            discount_amount=discount_amount
        )
        
        return True