# Existing Codebase

## Schema

```sql
CREATE TABLE orders_order (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id)
);

CREATE TABLE orders_orderitem (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders_order(id)
);
```

## Models

```python
from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet
from typing import Optional
import uuid


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'


class OrderQuerySet(QuerySet):
    def for_user(self, user: User) -> QuerySet:
        return self.filter(user=user)
    
    def active(self) -> QuerySet:
        return self.exclude(status=OrderStatus.CANCELLED)
    
    def by_status(self, status: str) -> QuerySet:
        return self.filter(status=status)


class OrderManager(models.Manager):
    def get_queryset(self) -> OrderQuerySet:
        return OrderQuerySet(self.model, using=self._db)
    
    def for_user(self, user: User) -> QuerySet:
        return self.get_queryset().for_user(user)


class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    order_number = models.CharField(max_length=20, unique=True)
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
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['order_number']),
        ]
    
    def __str__(self) -> str:
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)
    
    def _generate_order_number(self) -> str:
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    def is_owned_by(self, user: User) -> bool:
        return self.user_id == user.id
    
    @property
    def can_be_cancelled(self) -> bool:
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        indexes = [
            models.Index(fields=['order']),
        ]
    
    def __str__(self) -> str:
        return f"{self.quantity}x {self.product_name}"
    
    @property
    def total_price(self) -> models.DecimalField:
        return self.quantity * self.unit_price
```