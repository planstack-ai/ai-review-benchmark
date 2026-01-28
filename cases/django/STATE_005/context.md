# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    line_total DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Models

```python
from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError
from typing import Optional


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'
    PARTIALLY_CANCELLED = 'partially_cancelled', 'Partially Cancelled'


class ItemStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    CANCELLED = 'cancelled', 'Cancelled'


class OrderQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(status=OrderStatus.CANCELLED)
    
    def with_items(self):
        return self.prefetch_related('items')


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()


class Order(models.Model):
    customer_id = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderManager()
    
    class Meta:
        db_table = 'orders'
    
    def get_active_items_total(self) -> Decimal:
        return self.items.filter(status=ItemStatus.ACTIVE).aggregate(
            total=models.Sum('line_total')
        )['total'] or Decimal('0.00')
    
    def has_active_items(self) -> bool:
        return self.items.filter(status=ItemStatus.ACTIVE).exists()
    
    def recalculate_total(self) -> None:
        self.total_amount = self.get_active_items_total()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ItemStatus.choices, default=ItemStatus.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_items'
    
    def clean(self):
        if self.quantity <= 0:
            raise ValidationError('Quantity must be positive')
        
        expected_total = self.quantity * self.unit_price
        if self.line_total != expected_total:
            raise ValidationError('Line total must equal quantity × unit price')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
```