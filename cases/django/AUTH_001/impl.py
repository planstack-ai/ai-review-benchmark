from decimal import Decimal
from typing import List, Optional, Dict, Any
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Order, OrderItem, Product
from .exceptions import OrderNotFoundError, InsufficientStockError


class OrderService:
    
    def get_user_order(self, user: User, order_id: int) -> Order:
        try:
            order = Order.objects.get(pk=order_id)
            return order
        except ObjectDoesNotExist:
            raise OrderNotFoundError(f"Order with ID {order_id} not found")
    
    def get_user_orders(self, user: User, status: Optional[str] = None) -> List[Order]:
        queryset = user.orders.all()
        if status:
            queryset = queryset.filter(status=status)
        return list(queryset.order_by('-created_at'))
    
    @transaction.atomic
    def create_order(self, user: User, items_data: List[Dict[str, Any]]) -> Order:
        if not items_data:
            raise ValidationError("Order must contain at least one item")
        
        order = Order.objects.create(
            user=user,
            status='pending',
            total_amount=Decimal('0.00'),
            created_at=timezone.now()
        )
        
        total_amount = Decimal('0.00')
        
        for item_data in items_data:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity', 1)
            
            if not self._validate_item_data(product_id, quantity):
                order.delete()
                raise ValidationError("Invalid item data provided")
            
            product = Product.objects.get(pk=product_id)
            
            if not self._check_stock_availability(product, quantity):
                order.delete()
                raise InsufficientStockError(f"Insufficient stock for product {product.name}")
            
            item_total = product.price * quantity
            total_amount += item_total
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price,
                total_price=item_total
            )
            
            self._update_product_stock(product, quantity)
        
        order.total_amount = total_amount
        order.save()
        
        return order
    
    def update_order_status(self, user: User, order_id: int, new_status: str) -> Order:
        order = self.get_user_order(user, order_id)
        
        if not self._is_valid_status_transition(order.status, new_status):
            raise ValidationError(f"Cannot change status from {order.status} to {new_status}")
        
        order.status = new_status
        order.updated_at = timezone.now()
        order.save()
        
        return order
    
    def _validate_item_data(self, product_id: Optional[int], quantity: int) -> bool:
        if not product_id or quantity <= 0:
            return False
        
        try:
            Product.objects.get(pk=product_id)
            return True
        except ObjectDoesNotExist:
            return False
    
    def _check_stock_availability(self, product: Product, quantity: int) -> bool:
        return product.stock_quantity >= quantity
    
    def _update_product_stock(self, product: Product, quantity: int) -> None:
        product.stock_quantity -= quantity
        product.save()
    
    def _is_valid_status_transition(self, current_status: str, new_status: str) -> bool:
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['shipped', 'cancelled'],
            'shipped': ['delivered'],
            'delivered': [],
            'cancelled': []
        }
        
        return new_status in valid_transitions.get(current_status, [])