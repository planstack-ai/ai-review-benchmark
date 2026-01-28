from django.db import transaction
from django.core.exceptions import ValidationError
from typing import List, Optional, Dict, Any
from decimal import Decimal
from .models import Order, OrderItem, Product


class OrderService:
    """Service class for managing orders and order items."""
    
    def create_order(self, customer_id: int, items_data: List[Dict[str, Any]]) -> Order:
        """Create a new order with associated order items."""
        with transaction.atomic():
            order = Order.objects.create(
                customer_id=customer_id,
                status='pending',
                total_amount=Decimal('0.00')
            )
            
            total_amount = Decimal('0.00')
            for item_data in items_data:
                order_item = self._create_order_item(order.id, item_data)
                total_amount += order_item.subtotal
            
            order.total_amount = total_amount
            order.save()
            return order
    
    def _create_order_item(self, order_id: int, item_data: Dict[str, Any]) -> OrderItem:
        """Create an individual order item."""
        product = Product.objects.get(id=item_data['product_id'])
        quantity = item_data['quantity']
        
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")
        
        if product.stock_quantity < quantity:
            raise ValidationError(f"Insufficient stock for product {product.name}")
        
        unit_price = product.price
        subtotal = unit_price * quantity
        
        order_item = OrderItem.objects.create(
            order_id=order_id,
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal
        )
        
        product.stock_quantity -= quantity
        product.save()
        
        return order_item
    
    def update_order_status(self, order_id: int, new_status: str) -> Order:
        """Update the status of an existing order."""
        order = Order.objects.get(id=order_id)
        
        if not self._is_valid_status_transition(order.status, new_status):
            raise ValidationError(f"Invalid status transition from {order.status} to {new_status}")
        
        order.status = new_status
        order.save()
        return order
    
    def _is_valid_status_transition(self, current_status: str, new_status: str) -> bool:
        """Validate if status transition is allowed."""
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['shipped', 'cancelled'],
            'shipped': ['delivered'],
            'delivered': [],
            'cancelled': []
        }
        return new_status in valid_transitions.get(current_status, [])
    
    def get_order_items(self, order_id: int) -> List[OrderItem]:
        """Retrieve all items for a specific order."""
        return list(OrderItem.objects.filter(order_id=order_id).select_related('product'))
    
    def cancel_order(self, order_id: int) -> Order:
        """Cancel an order and restore product stock."""
        with transaction.atomic():
            order = Order.objects.get(id=order_id)
            
            if order.status not in ['pending', 'confirmed']:
                raise ValidationError("Cannot cancel order in current status")
            
            order_items = self.get_order_items(order_id)
            for item in order_items:
                self._restore_product_stock(item.product_id, item.quantity)
            
            order.status = 'cancelled'
            order.save()
            return order
    
    def _restore_product_stock(self, product_id: int, quantity: int) -> None:
        """Restore product stock when order is cancelled."""
        product = Product.objects.get(id=product_id)
        product.stock_quantity += quantity
        product.save()