# Existing Codebase

## Schema

```sql
CREATE TABLE orders_order (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    subtotal DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE coupons_coupon (
    id BIGINT PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    discount_type VARCHAR(20) NOT NULL,
    discount_value DECIMAL(10,2) NOT NULL,
    min_order_amount DECIMAL(10,2),
    max_discount_amount DECIMAL(10,2),
    is_active BOOLEAN NOT NULL DEFAULT true,
    valid_from TIMESTAMP NOT NULL,
    valid_until TIMESTAMP NOT NULL,
    usage_limit INTEGER,
    used_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE orders_ordercoupon (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders_order(id),
    coupon_id BIGINT NOT NULL REFERENCES coupons_coupon(id),
    discount_applied DECIMAL(10,2) NOT NULL,
    applied_at TIMESTAMP NOT NULL
);
```

## Models

```python
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from typing import Optional


class CouponQuerySet(models.QuerySet):
    def active(self):
        now = timezone.now()
        return self.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now
        )
    
    def available(self):
        return self.active().filter(
            models.Q(usage_limit__isnull=True) | 
            models.Q(used_count__lt=models.F('usage_limit'))
        )


class Coupon(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    
    objects = CouponQuerySet.as_manager()
    
    def calculate_discount(self, order_amount: Decimal) -> Decimal:
        if self.min_order_amount and order_amount < self.min_order_amount:
            return Decimal('0.00')
        
        if self.discount_type == 'percentage':
            discount = order_amount * (self.discount_value / Decimal('100'))
        else:
            discount = self.discount_value
        
        if self.max_discount_amount:
            discount = min(discount, self.max_discount_amount)
        
        return min(discount, order_amount)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_total(self) -> Decimal:
        return max(self.subtotal - self.discount_amount, Decimal('0.00'))
    
    def has_coupon_applied(self) -> bool:
        return self.ordercoupon_set.exists()


class OrderCoupon(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['order', 'coupon']
```