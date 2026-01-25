# Existing Codebase

## Schema

```sql
CREATE TABLE orders_order (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    shipping_cost DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE orders_orderitem (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders_order(id)
);
```

## Models

```python
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from typing import Optional


class ShippingConfig:
    FREE_SHIPPING_THRESHOLD = Decimal('5000.00')
    STANDARD_SHIPPING_COST = Decimal('500.00')


class OrderQuerySet(models.QuerySet):
    def with_items(self):
        return self.prefetch_related('items')
    
    def pending(self):
        return self.filter(status='pending')
    
    def completed(self):
        return self.filter(status='completed')


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)
    
    def with_items(self):
        return self.get_queryset().with_items()


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Order #{self.id} - {self.user.username}"

    def calculate_subtotal(self) -> Decimal:
        return sum(item.get_total_price() for item in self.items.all())

    def get_item_count(self) -> int:
        return self.items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['order', 'product']

    def get_total_price(self) -> Decimal:
        return self.quantity * self.unit_price

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"
```