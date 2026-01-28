from decimal import Decimal
from typing import Dict, List, Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.inventory.models import Product
from apps.orders.models import Order, OrderItem
from apps.cart.models import CartItem


class CheckoutService:
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self._cart_items: Optional[List[CartItem]] = None
    
    def process_checkout(self, shipping_address: Dict, payment_method: str) -> Order:
        cart_items = self._get_cart_items()
        if not cart_items:
            raise ValidationError("Cart is empty")
        
        self._validate_cart_items(cart_items)
        total_amount = self._calculate_total(cart_items)
        
        with transaction.atomic():
            order = self._create_order(shipping_address, payment_method, total_amount)
            self._create_order_items(order, cart_items)
            self._update_product_stock(cart_items)
            self._clear_cart()
            
        return order
    
    def _get_cart_items(self) -> List[CartItem]:
        if self._cart_items is None:
            self._cart_items = list(
                CartItem.objects.filter(user_id=self.user_id)
                .select_related('product')
                .order_by('created_at')
            )
        return self._cart_items
    
    def _validate_cart_items(self, cart_items: List[CartItem]) -> None:
        for item in cart_items:
            if not item.product.is_active:
                raise ValidationError(f"Product {item.product.name} is no longer available")
            
            if item.quantity <= 0:
                raise ValidationError("Invalid quantity in cart")
    
    def _calculate_total(self, cart_items: List[CartItem]) -> Decimal:
        total = Decimal('0.00')
        for item in cart_items:
            item_total = item.product.price * item.quantity
            total += item_total
        return total
    
    def _create_order(self, shipping_address: Dict, payment_method: str, total_amount: Decimal) -> Order:
        return Order.objects.create(
            user_id=self.user_id,
            status='pending',
            total_amount=total_amount,
            shipping_address=shipping_address,
            payment_method=payment_method,
            created_at=timezone.now()
        )
    
    def _create_order_items(self, order: Order, cart_items: List[CartItem]) -> None:
        order_items = []
        for cart_item in cart_items:
            order_item = OrderItem(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price,
                total_price=cart_item.product.price * cart_item.quantity
            )
            order_items.append(order_item)
        
        OrderItem.objects.bulk_create(order_items)
    
    def _update_product_stock(self, cart_items: List[CartItem]) -> None:
        for item in cart_items:
            product = item.product
            product.stock_quantity -= item.quantity
            product.save(update_fields=['stock_quantity'])
    
    def _clear_cart(self) -> None:
        CartItem.objects.filter(user_id=self.user_id).delete()
        self._cart_items = None