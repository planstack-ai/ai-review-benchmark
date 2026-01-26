# Existing Codebase

## Schema

```sql
CREATE TABLE orders_order (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE orders_orderitem (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders_order(id),
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);

CREATE TABLE inventory_stock (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL UNIQUE,
    quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0
);
```

## Models

```python
from decimal import Decimal
from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from typing import Optional


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    PROCESSING = 'processing', 'Processing'
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'


class OrderManager(models.Manager):
    def pending(self):
        return self.filter(status=OrderStatus.PENDING)
    
    def confirmed(self):
        return self.filter(status=OrderStatus.CONFIRMED)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(
        max_length=20, 
        choices=OrderStatus.choices, 
        default=OrderStatus.PENDING
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderManager()
    
    class Meta:
        db_table = 'orders_order'
        ordering = ['-created_at']
    
    def calculate_total(self) -> Decimal:
        return sum(item.subtotal for item in self.items.all())
    
    def can_be_cancelled(self) -> bool:
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'orders_orderitem'
        unique_together = ['order', 'product_id']
    
    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.unit_price


class StockManager(models.Manager):
    def reserve_stock(self, product_id: int, quantity: int) -> bool:
        with transaction.atomic():
            stock = self.select_for_update().get(product_id=product_id)
            available = stock.quantity - stock.reserved_quantity
            if available >= quantity:
                stock.reserved_quantity += quantity
                stock.save(update_fields=['reserved_quantity'])
                return True
            return False
    
    def release_reservation(self, product_id: int, quantity: int) -> None:
        with transaction.atomic():
            stock = self.select_for_update().get(product_id=product_id)
            stock.reserved_quantity = max(0, stock.reserved_quantity - quantity)
            stock.save(update_fields=['reserved_quantity'])
    
    def confirm_reservation(self, product_id: int, quantity: int) -> None:
        with transaction.atomic():
            stock = self.select_for_update().get(product_id=product_id)
            stock.quantity -= quantity
            stock.reserved_quantity -= quantity
            stock.save(update_fields=['quantity', 'reserved_quantity'])


class Stock(models.Model):
    product_id = models.PositiveIntegerField(unique=True)
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    
    objects = StockManager()
    
    class Meta:
        db_table = 'inventory_stock'
    
    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity
```