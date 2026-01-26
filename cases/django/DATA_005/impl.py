from decimal import Decimal
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Order, OrderItem, Product


class OrderHistoryService:
    """Service for managing order history and product data preservation."""
    
    def create_order_with_history(self, customer_id: int, items_data: List[Dict[str, Any]]) -> Order:
        """Create a new order while preserving current product information."""
        with transaction.atomic():
            order = Order.objects.create(
                customer_id=customer_id,
                created_at=timezone.now(),
                status='pending'
            )
            
            total_amount = Decimal('0.00')
            for item_data in items_data:
                order_item = self._create_order_item(order, item_data)
                total_amount += order_item.total_price
            
            order.total_amount = total_amount
            order.save()
            
            return order
    
    def _create_order_item(self, order: Order, item_data: Dict[str, Any]) -> OrderItem:
        """Create an order item with current product snapshot."""
        product_id = item_data['product_id']
        quantity = item_data['quantity']
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError(f"Product with ID {product_id} not found")
        
        if not self._validate_product_availability(product, quantity):
            raise ValidationError(f"Insufficient stock for product {product.name}")
        
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=product.price,
            total_price=product.price * quantity,
            snapshot_product_name=product.name,
            snapshot_product_description=product.description,
            snapshot_product_sku=product.sku
        )
        
        self._update_product_stock(product, quantity)
        return order_item
    
    def _validate_product_availability(self, product: Product, quantity: int) -> bool:
        """Validate if product has sufficient stock."""
        return product.stock_quantity >= quantity and product.is_active
    
    def _update_product_stock(self, product: Product, quantity: int) -> None:
        """Update product stock after order creation."""
        product.stock_quantity -= quantity
        product.save(update_fields=['stock_quantity'])
    
    def get_order_display_data(self, order_id: int) -> Dict[str, Any]:
        """Retrieve order data for display purposes."""
        try:
            order = Order.objects.select_related('customer').get(id=order_id)
        except Order.DoesNotExist:
            raise ValidationError(f"Order with ID {order_id} not found")
        
        order_items = self._get_order_items_display_data(order)
        
        return {
            'order_id': order.id,
            'customer_name': order.customer.full_name,
            'created_at': order.created_at,
            'status': order.status,
            'total_amount': order.total_amount,
            'items': order_items
        }
    
    def _get_order_items_display_data(self, order: Order) -> List[Dict[str, Any]]:
        """Get formatted order items data for display."""
        items = []
        order_items = OrderItem.objects.select_related('product').filter(order=order)
        
        for order_item in order_items:
            item_data = {
                'product_name': order_item.product.name,
                'quantity': order_item.quantity,
                'unit_price': order_item.unit_price,
                'total_price': order_item.total_price,
                'sku': order_item.product.sku
            }
            items.append(item_data)
        
        return items
    
    def generate_order_summary_report(self, order_ids: List[int]) -> List[Dict[str, Any]]:
        """Generate summary report for multiple orders."""
        summaries = []
        
        for order_id in order_ids:
            try:
                order_data = self.get_order_display_data(order_id)
                summary = self._create_order_summary(order_data)
                summaries.append(summary)
            except ValidationError:
                continue
        
        return summaries
    
    def _create_order_summary(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary from order data."""
        return {
            'order_id': order_data['order_id'],
            'customer_name': order_data['customer_name'],
            'item_count': len(order_data['items']),
            'total_amount': order_data['total_amount'],
            'order_date': order_data['created_at'].date()
        }