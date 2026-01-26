from datetime import date
from typing import Optional, Dict, Any
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from myapp.models import DeliveryOrder, Product, Customer


class DeliveryOrderService:
    """Service class for managing delivery orders and scheduling."""
    
    def __init__(self):
        self.minimum_order_value = Decimal('10.00')
        self.maximum_delivery_days = 30
    
    def create_delivery_order(
        self,
        customer: Customer,
        products: list[Dict[str, Any]],
        delivery_date: date,
        delivery_address: str,
        special_instructions: Optional[str] = None
    ) -> DeliveryOrder:
        """Create a new delivery order with validation."""
        
        self._validate_order_data(customer, products, delivery_date, delivery_address)
        
        total_amount = self._calculate_total_amount(products)
        
        with transaction.atomic():
            order = DeliveryOrder.objects.create(
                customer=customer,
                delivery_date=delivery_date,
                delivery_address=delivery_address,
                special_instructions=special_instructions,
                total_amount=total_amount,
                status='pending'
            )
            
            self._create_order_items(order, products)
            
        return order
    
    def update_delivery_date(self, order_id: int, new_delivery_date: date) -> DeliveryOrder:
        """Update the delivery date for an existing order."""
        
        order = DeliveryOrder.objects.get(id=order_id)
        
        if order.status in ['shipped', 'delivered', 'cancelled']:
            raise ValidationError("Cannot update delivery date for orders in final status")
        
        self._validate_delivery_date(new_delivery_date)
        
        order.delivery_date = new_delivery_date
        order.save()
        
        return order
    
    def _validate_order_data(
        self,
        customer: Customer,
        products: list[Dict[str, Any]],
        delivery_date: date,
        delivery_address: str
    ) -> None:
        """Validate all order data before creation."""
        
        if not customer.is_active:
            raise ValidationError("Customer account is not active")
        
        if not products:
            raise ValidationError("Order must contain at least one product")
        
        self._validate_delivery_date(delivery_date)
        self._validate_delivery_address(delivery_address)
        self._validate_products(products)
    
    def _validate_delivery_date(self, delivery_date: date) -> None:
        """Validate that delivery date meets business requirements."""
        
        if not delivery_date:
            raise ValidationError("Delivery date is required")
        
        max_future_date = timezone.now().date() + timezone.timedelta(days=self.maximum_delivery_days)
        if delivery_date > max_future_date:
            raise ValidationError(f"Delivery date cannot be more than {self.maximum_delivery_days} days in the future")
    
    def _validate_delivery_address(self, address: str) -> None:
        """Validate delivery address format and content."""
        
        if not address or len(address.strip()) < 10:
            raise ValidationError("Delivery address must be at least 10 characters long")
    
    def _validate_products(self, products: list[Dict[str, Any]]) -> None:
        """Validate product data and availability."""
        
        for product_data in products:
            product_id = product_data.get('product_id')
            quantity = product_data.get('quantity', 0)
            
            if not product_id:
                raise ValidationError("Product ID is required for all items")
            
            if quantity <= 0:
                raise ValidationError("Product quantity must be greater than zero")
            
            try:
                product = Product.objects.get(id=product_id, is_active=True)
                if product.stock_quantity < quantity:
                    raise ValidationError(f"Insufficient stock for product {product.name}")
            except Product.DoesNotExist:
                raise ValidationError(f"Product with ID {product_id} not found or inactive")
    
    def _calculate_total_amount(self, products: list[Dict[str, Any]]) -> Decimal:
        """Calculate total order amount including taxes."""
        
        total = Decimal('0.00')
        
        for product_data in products:
            product = Product.objects.get(id=product_data['product_id'])
            quantity = Decimal(str(product_data['quantity']))
            total += product.price * quantity
        
        if total < self.minimum_order_value:
            raise ValidationError(f"Order total must be at least {self.minimum_order_value}")
        
        return total
    
    def _create_order_items(self, order: DeliveryOrder, products: list[Dict[str, Any]]) -> None:
        """Create individual order items for the delivery order."""
        
        from myapp.models import DeliveryOrderItem
        
        for product_data in products:
            product = Product.objects.get(id=product_data['product_id'])
            
            DeliveryOrderItem.objects.create(
                order=order,
                product=product,
                quantity=product_data['quantity'],
                unit_price=product.price
            )