from decimal import Decimal
from typing import Optional, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Coupon, Order, CouponUsage


class CouponService:
    """Service class for handling coupon operations and validations."""
    
    def __init__(self):
        self.max_usage_per_user = 3
        self.min_order_amount = Decimal('10.00')
    
    def apply_coupon(self, user: User, coupon_code: str, order_amount: Decimal) -> Dict[str, Any]:
        """Apply a coupon to an order and return discount information."""
        try:
            with transaction.atomic():
                coupon = self._get_valid_coupon(coupon_code)
                if not coupon:
                    return {'success': False, 'error': 'Invalid coupon code'}
                
                validation_result = self._validate_coupon_usage(user, coupon, order_amount)
                if not validation_result['valid']:
                    return {'success': False, 'error': validation_result['error']}
                
                discount_amount = self._calculate_discount(coupon, order_amount)
                
                self._record_coupon_usage(user, coupon, discount_amount)
                
                return {
                    'success': True,
                    'discount_amount': discount_amount,
                    'coupon_type': coupon.discount_type,
                    'final_amount': order_amount - discount_amount
                }
        except Exception as e:
            return {'success': False, 'error': 'Failed to apply coupon'}
    
    def _get_valid_coupon(self, code: str) -> Optional[Coupon]:
        """Retrieve a valid coupon by code."""
        coupon = Coupon.objects.filter(code=code).first()
        
        if not coupon:
            return None
            
        if not coupon.is_active:
            return None
            
        current_time = timezone.now()
        if coupon.valid_from and current_time < coupon.valid_from:
            return None
            
        if coupon.valid_until and current_time > coupon.valid_until:
            return None
            
        return coupon
    
    def _validate_coupon_usage(self, user: User, coupon: Coupon, order_amount: Decimal) -> Dict[str, Any]:
        """Validate if the coupon can be used by the user."""
        if order_amount < self.min_order_amount:
            return {'valid': False, 'error': 'Order amount too low'}
        
        if coupon.minimum_amount and order_amount < coupon.minimum_amount:
            return {'valid': False, 'error': 'Order does not meet minimum amount requirement'}
        
        usage_count = self._get_user_coupon_usage_count(user, coupon)
        if usage_count >= coupon.max_uses_per_user:
            return {'valid': False, 'error': 'Coupon usage limit exceeded'}
        
        if coupon.total_uses >= coupon.max_total_uses:
            return {'valid': False, 'error': 'Coupon no longer available'}
        
        return {'valid': True}
    
    def _calculate_discount(self, coupon: Coupon, order_amount: Decimal) -> Decimal:
        """Calculate the discount amount based on coupon type."""
        if coupon.discount_type == 'percentage':
            discount = order_amount * (coupon.discount_value / 100)
            if coupon.max_discount_amount:
                discount = min(discount, coupon.max_discount_amount)
        else:
            discount = coupon.discount_value
        
        return min(discount, order_amount)
    
    def _get_user_coupon_usage_count(self, user: User, coupon: Coupon) -> int:
        """Get the number of times a user has used a specific coupon."""
        return CouponUsage.objects.filter(user=user, coupon=coupon).count()
    
    def _record_coupon_usage(self, user: User, coupon: Coupon, discount_amount: Decimal) -> None:
        """Record the coupon usage in the database."""
        CouponUsage.objects.create(
            user=user,
            coupon=coupon,
            discount_amount=discount_amount,
            used_at=timezone.now()
        )
        
        coupon.total_uses += 1
        coupon.save(update_fields=['total_uses'])