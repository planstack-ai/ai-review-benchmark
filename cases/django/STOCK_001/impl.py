from decimal import Decimal
from datetime import timedelta
from django.db import models, transaction
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.utils import timezone
from typing import Optional, Dict, Any
from .models import Product, Cart, CartItem, StockReservation


class StockAllocationService:
    
    def __init__(self):
        self.reservation_timeout_minutes = 15
    
    def add_item_to_cart(self, cart: Cart, product: Product, quantity: int) -> CartItem:
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")
        
        if not self._check_stock_availability(product, quantity):
            raise ValidationError(f"Insufficient stock for {product.name}")
        
        with transaction.atomic():
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            self._reserve_stock_for_item(product, quantity, cart.user_id)
            
        return cart_item
    
    def remove_item_from_cart(self, cart_item: CartItem) -> None:
        with transaction.atomic():
            self._release_stock_reservation(
                cart_item.product, 
                cart_item.quantity, 
                cart_item.cart.user_id
            )
            cart_item.delete()
    
    def process_checkout(self, cart: Cart) -> Dict[str, Any]:
        if not cart.items.exists():
            raise ValidationError("Cart is empty")
        
        total_amount = self._calculate_cart_total(cart)
        
        with transaction.atomic():
            for item in cart.items.all():
                if not self._validate_reserved_stock(item.product, item.quantity, cart.user_id):
                    raise ValidationError(f"Stock reservation expired for {item.product.name}")
            
            order_data = {
                'user_id': cart.user_id,
                'total_amount': total_amount,
                'items': list(cart.items.values('product_id', 'quantity', 'price'))
            }
            
        return order_data
    
    def confirm_payment(self, order_data: Dict[str, Any]) -> bool:
        with transaction.atomic():
            for item_data in order_data['items']:
                product = Product.objects.get(id=item_data['product_id'])
                self._finalize_stock_allocation(product, item_data['quantity'])
                
            self._clear_user_reservations(order_data['user_id'])
            
        return True
    
    def _check_stock_availability(self, product: Product, quantity: int) -> bool:
        available_stock = product.stock_quantity - self._get_reserved_quantity(product)
        return available_stock >= quantity
    
    def _reserve_stock_for_item(self, product: Product, quantity: int, user_id: int) -> None:
        StockReservation.objects.create(
            product=product,
            user_id=user_id,
            quantity=quantity,
            expires_at=timezone.now() + timedelta(minutes=self.reservation_timeout_minutes)
        )
    
    def _release_stock_reservation(self, product: Product, quantity: int, user_id: int) -> None:
        reservations = StockReservation.objects.filter(
            product=product,
            user_id=user_id
        ).order_by('created_at')
        
        remaining_to_release = quantity
        for reservation in reservations:
            if remaining_to_release <= 0:
                break
                
            if reservation.quantity <= remaining_to_release:
                remaining_to_release -= reservation.quantity
                reservation.delete()
            else:
                reservation.quantity -= remaining_to_release
                reservation.save()
                remaining_to_release = 0
    
    def _get_reserved_quantity(self, product: Product) -> int:
        return StockReservation.objects.filter(
            product=product,
            expires_at__gt=timezone.now()
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0
    
    def _validate_reserved_stock(self, product: Product, quantity: int, user_id: int) -> bool:
        reserved_quantity = StockReservation.objects.filter(
            product=product,
            user_id=user_id,
            expires_at__gt=timezone.now()
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        return reserved_quantity >= quantity
    
    def _finalize_stock_allocation(self, product: Product, quantity: int) -> None:
        product.stock_quantity -= quantity
        product.save()
    
    def _calculate_cart_total(self, cart: Cart) -> Decimal:
        return sum(item.quantity * item.product.price for item in cart.items.all())
    
    def _clear_user_reservations(self, user_id: int) -> None:
        StockReservation.objects.filter(user_id=user_id).delete()