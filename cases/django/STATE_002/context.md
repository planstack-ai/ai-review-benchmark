# Existing Codebase

## Schema

```sql
CREATE TABLE orders_order (
    id BIGINT PRIMARY KEY,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE orders_shipment (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders_order(id),
    tracking_number VARCHAR(50) UNIQUE,
    shipped_at TIMESTAMP,
    carrier VARCHAR(50),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

## Models

```python
from django.db import models
from django.utils import timezone
from typing import Optional


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    PROCESSING = 'processing', 'Processing'
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'


class OrderQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(status=OrderStatus.CANCELLED)
    
    def shipped(self):
        return self.filter(status=OrderStatus.SHIPPED)
    
    def pending_shipment(self):
        return self.filter(
            status__in=[OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PROCESSING]
        )


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def shipped(self):
        return self.get_queryset().shipped()
    
    def pending_shipment(self):
        return self.get_queryset().pending_shipment()


class Order(models.Model):
    order_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE)
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
    
    def __str__(self) -> str:
        return f"Order {self.order_number}"
    
    @property
    def is_shipped(self) -> bool:
        return hasattr(self, 'shipment') and self.shipment.shipped_at is not None
    
    def update_status(self, new_status: OrderStatus) -> None:
        self.status = new_status
        self.updated_at = timezone.now()
        self.save(update_fields=['status', 'updated_at'])


class Shipment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipment')
    tracking_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    carrier = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders_shipment'
    
    def __str__(self) -> str:
        return f"Shipment for {self.order.order_number}"
    
    def mark_as_shipped(self, tracking_number: str, carrier: str = '') -> None:
        self.tracking_number = tracking_number
        self.carrier = carrier
        self.shipped_at = timezone.now()
        self.save()
        
        self.order.update_status(OrderStatus.SHIPPED)
```