# Existing Codebase

## Schema

```sql
CREATE TABLE inventory_item (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    price DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE orders_order (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE orders_orderitem (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders_order(id),
    item_id INTEGER NOT NULL REFERENCES inventory_item(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

## Models

```python
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class ActiveItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Item(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    active = ActiveItemManager()

    class Meta:
        db_table = 'inventory_item'

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"

    def is_in_stock(self) -> bool:
        return self.quantity > 0

    def can_fulfill_quantity(self, requested_quantity: int) -> bool:
        return self.quantity >= requested_quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders_order'

    def __str__(self) -> str:
        return f"Order {self.order_number}"

    def calculate_total(self) -> Decimal:
        return sum(item.get_total_price() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders_orderitem'
        unique_together = ['order', 'item']

    def __str__(self) -> str:
        return f"{self.quantity}x {self.item.name}"

    def get_total_price(self) -> Decimal:
        return self.quantity * self.unit_price

    def clean(self):
        if hasattr(self, 'item') and self.item:
            if not self.item.is_active:
                raise ValidationError("Cannot order inactive items.")
```