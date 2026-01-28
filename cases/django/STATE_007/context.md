# Existing Codebase

## Schema

```sql
CREATE TABLE delivery_order (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE delivery_status_log (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES delivery_order(id),
    from_status VARCHAR(20),
    to_status VARCHAR(20) NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    changed_by_id INTEGER
);
```

## Models

```python
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from typing import Optional

User = get_user_model()


class DeliveryStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    PREPARING = 'preparing', 'Preparing'
    SHIPPED = 'shipped', 'Shipped'
    OUT_FOR_DELIVERY = 'out_for_delivery', 'Out for Delivery'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'
    RETURNED = 'returned', 'Returned'


class DeliveryOrderQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(status__in=[DeliveryStatus.CANCELLED, DeliveryStatus.RETURNED])
    
    def in_transit(self):
        return self.filter(status__in=[
            DeliveryStatus.SHIPPED, 
            DeliveryStatus.OUT_FOR_DELIVERY
        ])


class DeliveryOrderManager(models.Manager):
    def get_queryset(self):
        return DeliveryOrderQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def in_transit(self):
        return self.get_queryset().in_transit()


class DeliveryOrder(models.Model):
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = DeliveryOrderManager()
    
    class Meta:
        db_table = 'delivery_order'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Order {self.order_number} - {self.get_status_display()}"
    
    @property
    def status_history(self):
        return self.status_logs.all().order_by('changed_at')
    
    def get_valid_next_statuses(self) -> list[str]:
        status_transitions = {
            DeliveryStatus.PENDING: [DeliveryStatus.CONFIRMED, DeliveryStatus.CANCELLED],
            DeliveryStatus.CONFIRMED: [DeliveryStatus.PREPARING, DeliveryStatus.CANCELLED],
            DeliveryStatus.PREPARING: [DeliveryStatus.SHIPPED, DeliveryStatus.CANCELLED],
            DeliveryStatus.SHIPPED: [DeliveryStatus.OUT_FOR_DELIVERY, DeliveryStatus.RETURNED],
            DeliveryStatus.OUT_FOR_DELIVERY: [DeliveryStatus.DELIVERED, DeliveryStatus.RETURNED],
            DeliveryStatus.DELIVERED: [],
            DeliveryStatus.CANCELLED: [],
            DeliveryStatus.RETURNED: [],
        }
        return status_transitions.get(self.status, [])


class DeliveryStatusLog(models.Model):
    order = models.ForeignKey(
        DeliveryOrder,
        on_delete=models.CASCADE,
        related_name='status_logs'
    )
    from_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        null=True,
        blank=True
    )
    to_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices
    )
    changed_at = models.DateTimeField(default=timezone.now)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'delivery_status_log'
        ordering = ['-changed_at']
    
    def __str__(self) -> str:
        return f"{self.order.order_number}: {self.from_status} → {self.to_status}"
```