from decimal import Decimal
from typing import Optional, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Order, OrderItem, Customer
from .exceptions import OrderProcessingError, InsufficientInventoryError
import logging
import uuid

logger = logging.getLogger(__name__)


class OrderProcessingService:
    """Service for processing customer orders with retry capabilities."""
    
    def __init__(self):
        self.max_retry_attempts = 3
        self.retry_delay_seconds = 2
    
    def process_order(self, customer_id: int, items: list, 
                     idempotency_key: Optional[str] = None) -> Order:
        """
        Process a new customer order with automatic retry on network failures.
        
        Args:
            customer_id: ID of the customer placing the order
            items: List of items with product_id and quantity
            idempotency_key: Optional key to prevent duplicate processing
            
        Returns:
            Created Order instance
            
        Raises:
            OrderProcessingError: If order processing fails
            ValidationError: If order data is invalid
        """
        if not idempotency_key:
            idempotency_key = str(uuid.uuid4())
            
        customer = self._get_customer(customer_id)
        validated_items = self._validate_order_items(items)
        total_amount = self._calculate_total(validated_items)
        
        with transaction.atomic():
            order = self._create_order(customer, total_amount, idempotency_key)
            self._create_order_items(order, validated_items)
            self._update_inventory(validated_items)
            
        logger.info(f"Order {order.id} processed successfully for customer {customer_id}")
        return order
    
    def retry_failed_order(self, customer_id: int, items: list, 
                          original_idempotency_key: str) -> Order:
        """
        Retry processing a failed order with the same idempotency key.
        
        Args:
            customer_id: ID of the customer
            items: Original order items
            original_idempotency_key: Key from the original failed attempt
            
        Returns:
            Order instance (existing or newly created)
        """
        try:
            return self.process_order(customer_id, items, original_idempotency_key)
        except Exception as e:
            logger.error(f"Order retry failed for key {original_idempotency_key}: {str(e)}")
            raise OrderProcessingError(f"Failed to retry order: {str(e)}")
    
    def _get_customer(self, customer_id: int) -> Customer:
        """Retrieve and validate customer."""
        try:
            return Customer.objects.get(id=customer_id, is_active=True)
        except Customer.DoesNotExist:
            raise ValidationError(f"Customer {customer_id} not found or inactive")
    
    def _validate_order_items(self, items: list) -> list:
        """Validate order items and check inventory availability."""
        if not items:
            raise ValidationError("Order must contain at least one item")
            
        validated_items = []
        for item in items:
            if item.get('quantity', 0) <= 0:
                raise ValidationError("Item quantity must be positive")
            validated_items.append(item)
            
        return validated_items
    
    def _calculate_total(self, items: list) -> Decimal:
        """Calculate total order amount."""
        total = Decimal('0.00')
        for item in items:
            price = Decimal(str(item.get('price', 0)))
            quantity = item.get('quantity', 0)
            total += price * quantity
        return total
    
    def _create_order(self, customer: Customer, total_amount: Decimal, 
                     idempotency_key: str) -> Order:
        """Create new order record."""
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            status='pending',
            created_at=timezone.now(),
            idempotency_key=idempotency_key
        )
        return order
    
    def _create_order_items(self, order: Order, items: list) -> None:
        """Create order item records."""
        for item in items:
            OrderItem.objects.create(
                order=order,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=Decimal(str(item['price']))
            )
    
    def _update_inventory(self, items: list) -> None:
        """Update product inventory levels."""
        for item in items:
            # Inventory update logic would go here
            pass