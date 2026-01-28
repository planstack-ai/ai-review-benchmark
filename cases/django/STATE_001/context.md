# Existing Codebase

## Schema

```python
# orders/migrations/0001_initial.py
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    
    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('order_number', models.CharField(max_length=20, unique=True)),
                ('status', models.CharField(max_length=20, default='pending')),
                ('total_amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
```

## Models

```python
# orders/models.py
from django.db import models
from django.core.exceptions import ValidationError
from typing import Dict, Set


class OrderStatus:
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'
    
    CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (PROCESSING, 'Processing'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
        (REFUNDED, 'Refunded'),
    ]
    
    VALID_TRANSITIONS: Dict[str, Set[str]] = {
        PENDING: {CONFIRMED, CANCELLED},
        CONFIRMED: {PROCESSING, CANCELLED},
        PROCESSING: {SHIPPED, CANCELLED},
        SHIPPED: {DELIVERED, CANCELLED},
        DELIVERED: {REFUNDED},
        CANCELLED: set(),
        REFUNDED: set(),
    }


class OrderQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(status__in=[OrderStatus.CANCELLED, OrderStatus.REFUNDED])
    
    def by_status(self, status: str):
        return self.filter(status=status)
    
    def pending_orders(self):
        return self.filter(status=OrderStatus.PENDING)


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def by_status(self, status: str):
        return self.get_queryset().by_status(status)


class Order(models.Model):
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.CHOICES,
        default=OrderStatus.PENDING
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderManager()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Order {self.order_number} - {self.get_status_display()}"
    
    def is_active(self) -> bool:
        return self.status not in [OrderStatus.CANCELLED, OrderStatus.REFUNDED]
    
    def can_be_cancelled(self) -> bool:
        return self.status in [
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.PROCESSING,
            OrderStatus.SHIPPED
        ]
    
    def get_allowed_transitions(self) -> Set[str]:
        return OrderStatus.VALID_TRANSITIONS.get(self.status, set())
```