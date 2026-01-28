# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    payment_method VARCHAR(50),
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

## Models

```python
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    EXPIRED = 'expired', 'Expired'
    CANCELLED = 'cancelled', 'Cancelled'


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    REJECTED = 'rejected', 'Rejected'


class OrderQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status__in=[OrderStatus.PENDING, OrderStatus.CONFIRMED])
    
    def expired(self):
        return self.filter(expires_at__lt=timezone.now())
    
    def pending_payment(self):
        return self.filter(status=OrderStatus.PENDING)


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def expired(self):
        return self.get_queryset().expired()
    
    def pending_payment(self):
        return self.get_queryset().pending_payment()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderManager()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Order #{self.id} - {self.status}"
    
    @property
    def is_expired(self) -> bool:
        return (
            self.expires_at is not None 
            and timezone.now() > self.expires_at
        )
    
    def set_expiration(self, minutes: int = 30) -> None:
        self.expires_at = timezone.now() + timedelta(minutes=minutes)
        self.save(update_fields=['expires_at'])


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    payment_method = models.CharField(max_length=50, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Payment #{self.id} for Order #{self.order_id}"
    
    def mark_completed(self) -> None:
        self.status = PaymentStatus.COMPLETED
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])
    
    def mark_failed(self) -> None:
        self.status = PaymentStatus.FAILED
        self.save(update_fields=['status'])
```