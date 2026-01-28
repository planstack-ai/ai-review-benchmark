# Existing Codebase

## Schema

```sql
CREATE TABLE shipping_carriers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    api_endpoint VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE shipping_rates (
    id SERIAL PRIMARY KEY,
    carrier_id INTEGER REFERENCES shipping_carriers(id),
    service_type VARCHAR(50) NOT NULL,
    base_rate DECIMAL(10,2) NOT NULL,
    weight_multiplier DECIMAL(5,2) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_email VARCHAR(255) NOT NULL,
    shipping_address TEXT NOT NULL,
    total_weight DECIMAL(8,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    shipping_cost DECIMAL(10,2),
    tracking_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Models

```python
from decimal import Decimal
from typing import Optional
from django.db import models
from django.core.exceptions import ValidationError


class ShippingCarrierManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)
    
    def get_primary_carrier(self):
        return self.active().filter(name='FedEx').first()


class ShippingCarrier(models.Model):
    name = models.CharField(max_length=100)
    api_endpoint = models.URLField()
    api_key = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ShippingCarrierManager()
    
    class Meta:
        db_table = 'shipping_carriers'
    
    def __str__(self) -> str:
        return self.name


class ShippingRate(models.Model):
    SERVICE_TYPES = [
        ('standard', 'Standard'),
        ('express', 'Express'),
        ('overnight', 'Overnight'),
    ]
    
    carrier = models.ForeignKey(ShippingCarrier, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    base_rate = models.DecimalField(max_digits=10, decimal_places=2)
    weight_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.0'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'shipping_rates'
        unique_together = ['carrier', 'service_type']
    
    def calculate_cost(self, weight: Decimal) -> Decimal:
        return self.base_rate + (weight * self.weight_multiplier)


class OrderManager(models.Manager):
    def pending_shipment(self):
        return self.filter(status='pending', shipping_cost__isnull=True)
    
    def with_tracking(self):
        return self.exclude(tracking_number__isnull=True)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer_email = models.EmailField()
    shipping_address = models.TextField()
    total_weight = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = OrderManager()
    
    class Meta:
        db_table = 'orders'
    
    def clean(self):
        if self.total_weight <= 0:
            raise ValidationError('Total weight must be positive')
    
    def is_ready_for_shipment(self) -> bool:
        return self.status == 'pending' and self.shipping_cost is not None
    
    def mark_as_shipped(self, tracking_number: str) -> None:
        self.status = 'shipped'
        self.tracking_number = tracking_number
        self.save(update_fields=['status', 'tracking_number'])
```