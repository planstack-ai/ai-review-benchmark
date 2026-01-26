# Existing Codebase

## Schema

```sql
CREATE TABLE delivery_orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    delivery_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE delivery_slots (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    capacity INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE
);
```

## Models

```python
from datetime import date, datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from typing import Optional


class DeliverySlot(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['date', 'start_time']
        ordering = ['date', 'start_time']

    def __str__(self) -> str:
        return f"{self.date} {self.start_time}-{self.end_time}"

    @property
    def is_available(self) -> bool:
        return self.is_active and self.date >= timezone.now().date()


class DeliveryOrderQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status='pending')
    
    def scheduled_for_date(self, target_date: date):
        return self.filter(delivery_date=target_date)
    
    def upcoming(self):
        return self.filter(delivery_date__gte=timezone.now().date())


class DeliveryOrderManager(models.Manager):
    def get_queryset(self):
        return DeliveryOrderQuerySet(self.model, using=self._db)
    
    def pending(self):
        return self.get_queryset().pending()
    
    def upcoming(self):
        return self.get_queryset().upcoming()


class DeliveryOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    customer_id = models.PositiveIntegerField()
    delivery_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = DeliveryOrderManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['delivery_date', 'status']),
            models.Index(fields=['customer_id']),
        ]

    def __str__(self) -> str:
        return f"Order {self.id} - {self.delivery_date}"

    def get_delivery_window(self) -> Optional[str]:
        if hasattr(self, 'delivery_slot'):
            slot = self.delivery_slot
            return f"{slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}"
        return None

    @property
    def is_upcoming(self) -> bool:
        return self.delivery_date >= timezone.now().date()

    @property
    def days_until_delivery(self) -> int:
        today = timezone.now().date()
        return (self.delivery_date - today).days
```