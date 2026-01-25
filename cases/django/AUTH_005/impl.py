from decimal import Decimal
from typing import Optional
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone


class PricingService:
    """Service class for handling product pricing logic including member discounts."""
    
    def __init__(self):
        self.member_discount_rate = Decimal('0.15')
        self.bulk_discount_threshold = 10
        self.bulk_discount_rate = Decimal('0.10')
    
    def calculate_product_price(self, product_id: int, quantity: int = 1, 
                              user: Optional[User] = None) -> Decimal:
        """Calculate final price for a product including applicable discounts."""
        base_price = self._get_base_price(product_id)
        
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero")
        
        total_price = base_price * quantity
        
        # Apply member discount if applicable
        member_price = self._apply_member_discount(total_price, user)
        
        # Apply bulk discount if applicable
        final_price = self._apply_bulk_discount(member_price, quantity)
        
        return final_price.quantize(Decimal('0.01'))
    
    def get_pricing_breakdown(self, product_id: int, quantity: int = 1,
                            user: Optional[User] = None) -> dict:
        """Get detailed pricing breakdown for transparency."""
        base_price = self._get_base_price(product_id)
        total_base = base_price * quantity
        
        breakdown = {
            'base_price': base_price,
            'quantity': quantity,
            'subtotal': total_base,
            'member_discount': Decimal('0.00'),
            'bulk_discount': Decimal('0.00'),
            'final_price': total_base
        }
        
        # Calculate member discount
        if self._is_eligible_for_member_pricing(user):
            member_discount = total_base * self.member_discount_rate
            breakdown['member_discount'] = member_discount
            breakdown['final_price'] -= member_discount
        
        # Calculate bulk discount
        if quantity >= self.bulk_discount_threshold:
            bulk_discount = breakdown['final_price'] * self.bulk_discount_rate
            breakdown['bulk_discount'] = bulk_discount
            breakdown['final_price'] -= bulk_discount
        
        breakdown['final_price'] = breakdown['final_price'].quantize(Decimal('0.01'))
        return breakdown
    
    def _get_base_price(self, product_id: int) -> Decimal:
        """Retrieve base price for a product."""
        from .models import Product
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            return product.base_price
        except Product.DoesNotExist:
            raise ValidationError(f"Product with ID {product_id} not found")
    
    def _apply_member_discount(self, price: Decimal, user: Optional[User]) -> Decimal:
        """Apply member discount to the given price."""
        if user and hasattr(user, 'membership'):
            discount_amount = price * self.member_discount_rate
            return price - discount_amount
        return price
    
    def _apply_bulk_discount(self, price: Decimal, quantity: int) -> Decimal:
        """Apply bulk discount for large quantity orders."""
        if quantity >= self.bulk_discount_threshold:
            discount_amount = price * self.bulk_discount_rate
            return price - discount_amount
        return price
    
    def _is_eligible_for_member_pricing(self, user: Optional[User]) -> bool:
        """Check if user is eligible for member pricing."""
        if not user:
            return False
        
        return (user.is_authenticated and 
                hasattr(user, 'membership') and 
                user.membership.is_active and
                user.membership.expires_at > timezone.now())