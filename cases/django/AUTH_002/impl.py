from decimal import Decimal
from typing import Optional, List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.models import User
from .models import Cart, CartItem, Product


class CartService:
    """Service class for managing shopping cart operations."""
    
    def __init__(self, user: User):
        self.user = user
    
    def add_item_to_cart(self, cart_id: int, product_id: int, quantity: int = 1) -> Dict[str, Any]:
        """Add an item to the specified cart."""
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")
        
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
            cart = Cart.objects.get(pk=cart_id)
            
            if not self._validate_product_availability(product, quantity):
                raise ValidationError("Insufficient stock available")
            
            with transaction.atomic():
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': quantity, 'unit_price': product.price}
                )
                
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
                
                self._update_cart_totals(cart)
                
            return {
                'success': True,
                'cart_item_id': cart_item.id,
                'total_quantity': cart_item.quantity,
                'cart_total': cart.total_amount
            }
            
        except (Product.DoesNotExist, Cart.DoesNotExist):
            raise ValidationError("Product or cart not found")
    
    def remove_item_from_cart(self, cart_id: int, product_id: int, quantity: Optional[int] = None) -> Dict[str, Any]:
        """Remove item or reduce quantity in the specified cart."""
        try:
            cart = Cart.objects.get(pk=cart_id)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            
            with transaction.atomic():
                if quantity is None or quantity >= cart_item.quantity:
                    cart_item.delete()
                    remaining_quantity = 0
                else:
                    cart_item.quantity -= quantity
                    cart_item.save()
                    remaining_quantity = cart_item.quantity
                
                self._update_cart_totals(cart)
                
            return {
                'success': True,
                'remaining_quantity': remaining_quantity,
                'cart_total': cart.total_amount
            }
            
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            raise ValidationError("Cart or item not found")
    
    def get_cart_summary(self, cart_id: int) -> Dict[str, Any]:
        """Get comprehensive cart summary with items and totals."""
        try:
            cart = Cart.objects.prefetch_related('items__product').get(pk=cart_id)
            
            items = []
            for cart_item in cart.items.all():
                items.append({
                    'product_id': cart_item.product.id,
                    'product_name': cart_item.product.name,
                    'quantity': cart_item.quantity,
                    'unit_price': cart_item.unit_price,
                    'subtotal': cart_item.quantity * cart_item.unit_price
                })
            
            return {
                'cart_id': cart.id,
                'items': items,
                'item_count': len(items),
                'total_amount': cart.total_amount,
                'last_updated': cart.updated_at
            }
            
        except Cart.DoesNotExist:
            raise ValidationError("Cart not found")
    
    def _validate_product_availability(self, product: Product, requested_quantity: int) -> bool:
        """Check if requested quantity is available in stock."""
        return product.stock_quantity >= requested_quantity
    
    def _update_cart_totals(self, cart: Cart) -> None:
        """Recalculate and update cart total amounts."""
        total = Decimal('0.00')
        for item in cart.items.all():
            total += item.quantity * item.unit_price
        
        cart.total_amount = total
        cart.save(update_fields=['total_amount', 'updated_at'])
    
    def _get_or_create_user_cart(self) -> Cart:
        """Get existing cart or create new one for the user."""
        cart, created = Cart.objects.get_or_create(
            user=self.user,
            is_active=True,
            defaults={'total_amount': Decimal('0.00')}
        )
        return cart