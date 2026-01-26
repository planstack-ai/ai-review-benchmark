# Existing Codebase

## Schema

```sql
CREATE TABLE orders_order (
    id BIGINT PRIMARY KEY,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id BIGINT NOT NULL,
    order_date DATE NOT NULL,
    estimated_delivery_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE orders_holiday (
    id BIGINT PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true
);
```

## Models

```python
from datetime import date, datetime, timedelta
from typing import Optional

from django.db import models
from django.utils import timezone


class HolidayManager(models.Manager):
    def active_holidays(self) -> models.QuerySet['Holiday']:
        return self.filter(is_active=True)
    
    def holidays_between(self, start_date: date, end_date: date) -> models.QuerySet['Holiday']:
        return self.active_holidays().filter(
            date__gte=start_date,
            date__lte=end_date
        )


class Holiday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    objects = HolidayManager()
    
    class Meta:
        ordering = ['date']
    
    def __str__(self) -> str:
        return f"{self.name} ({self.date})"


class OrderQuerySet(models.QuerySet):
    def pending(self) -> 'OrderQuerySet':
        return self.filter(status='pending')
    
    def with_delivery_dates(self) -> 'OrderQuerySet':
        return self.exclude(estimated_delivery_date__isnull=True)


class OrderManager(models.Manager):
    def get_queryset(self) -> OrderQuerySet:
        return OrderQuerySet(self.model, using=self._db)
    
    def pending(self) -> OrderQuerySet:
        return self.get_queryset().pending()


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'
    
    order_number = models.CharField(max_length=20, unique=True)
    customer_id = models.BigIntegerField()
    order_date = models.DateField(default=timezone.now)
    estimated_delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderManager()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Order {self.order_number}"
    
    @property
    def is_overdue(self) -> bool:
        if not self.estimated_delivery_date:
            return False
        return (
            self.estimated_delivery_date < timezone.now().date() 
            and self.status not in [self.Status.DELIVERED, self.Status.CANCELLED]
        )


# Business constants
STANDARD_PROCESSING_DAYS = 3
EXPRESS_PROCESSING_DAYS = 1
WEEKEND_DAYS = {5, 6}  # Saturday=5, Sunday=6 in Python's weekday()
```