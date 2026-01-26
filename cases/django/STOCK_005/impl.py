from decimal import Decimal
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth.models import User
from myapp.models import Order, OrderItem, Product


class OrderValidationService:
    """Service class for validating and processing orders."""
    
    def __init__(self):
        self.min_quantity_validator = MinValueValidator(0)
        self.max_items_per_order = 50
    
    def validate_and_create_order(self, user: User, items_data: List[Dict[str, Any]]) -> Order:
        """
        Validates order data and creates a new order with items.
        
        Args:
            user: The user placing the order
            items_data: List of dictionaries containing item data
            
        Returns:
            Created Order instance
            
        Raises:
            ValidationError: If validation fails
        """
        self._validate_order_structure(items_data)
        
        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                status='pending',
                created_at=timezone.now()
            )
            
            total_amount = Decimal('0.00')
            
            for item_data in items_data:
                order_item = self._create_order_item(order, item_data)
                total_amount += order_item.total_price
            
            order.total_amount = total_amount
            order.save()
            
            return order
    
    def _validate_order_structure(self, items_data: List[Dict[str, Any]]) -> None:
        """Validates the basic structure of order data."""
        if not items_data:
            raise ValidationError("Order must contain at least one item")
        
        if len(items_data) > self.max_items_per_order:
            raise ValidationError(f"Order cannot contain more than {self.max_items_per_order} items")
        
        required_fields = ['product_id', 'quantity']
        for item_data in items_data:
            for field in required_fields:
                if field not in item_data:
                    raise ValidationError(f"Missing required field: {field}")
    
    def _create_order_item(self, order: Order, item_data: Dict[str, Any]) -> OrderItem:
        """Creates and validates a single order item."""
        product_id = item_data['product_id']
        quantity = item_data['quantity']
        
        product = self._get_validated_product(product_id)
        self._validate_item_quantity(quantity)
        self._validate_stock_availability(product, quantity)
        
        unit_price = product.price
        total_price = unit_price * Decimal(str(quantity))
        
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price
        )
        
        return order_item
    
    def _get_validated_product(self, product_id: int) -> Product:
        """Retrieves and validates product exists and is available."""
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            raise ValidationError(f"Product with id {product_id} not found or inactive")
        
        return product
    
    def _validate_item_quantity(self, quantity: Any) -> None:
        """Validates that item quantity meets requirements."""
        try:
            quantity_decimal = Decimal(str(quantity))
            self.min_quantity_validator(quantity_decimal)
        except (ValueError, TypeError):
            raise ValidationError("Quantity must be a valid number")
        except ValidationError:
            raise ValidationError("Quantity must be greater than or equal to minimum allowed")
    
    def _validate_stock_availability(self, product: Product, quantity: int) -> None:
        """Validates that sufficient stock is available."""
        if product.stock_quantity < quantity:
            raise ValidationError(
                f"Insufficient stock for product {product.name}. "
                f"Available: {product.stock_quantity}, Requested: {quantity}"
            )
    
    def get_order_summary(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Returns a summary of the order for review."""
        try:
            order = Order.objects.select_related('user').prefetch_related(
                'items__product'
            ).get(id=order_id)
        except Order.DoesNotExist:
            return None
        
        items_summary = []
        for item in order.items.all():
            items_summary.append({
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total_price': item.total_price
            })
        
        return {
            'order_id': order.id,
            'user': order.user.username,
            'status': order.status,
            'total_amount': order.total_amount,
            'items': items_summary,
            'created_at': order.created_at
        }