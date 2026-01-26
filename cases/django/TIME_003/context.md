# Existing Codebase

## Schema

```sql
CREATE TABLE coupons_coupon (
    id BIGINT PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    discount_percent DECIMAL(5,2),
    discount_amount DECIMAL(10,2),
    expiry_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders_order (
    id BIGINT PRIMARY KEY,
    coupon_id BIGINT REFERENCES coupons_coupon(id),
    total_amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Models

```python
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from django.db import models
from django.utils import timezone


class CouponQuerySet(models.QuerySet):
    def active(self) -> "CouponQuerySet":
        return self.filter(is_active=True)
    
    def by_code(self, code: str) -> "CouponQuerySet":
        return self.filter(code__iexact=code)


class CouponManager(models.Manager):
    def get_queryset(self) -> CouponQuerySet:
        return CouponQuerySet(self.model, using=self._db)
    
    def active(self) -> CouponQuerySet:
        return self.get_queryset().active()
    
    def find_by_code(self, code: str) -> Optional["Coupon"]:
        try:
            return self.active().by_code(code).get()
        except self.model.DoesNotExist:
            return None


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CouponManager()
    
    class Meta:
        db_table = "coupons_coupon"
    
    def __str__(self) -> str:
        return self.code
    
    @property
    def has_expiry(self) -> bool:
        return self.expiry_date is not None
    
    def calculate_discount(self, amount: Decimal) -> Decimal:
        if self.discount_percent:
            return amount * (self.discount_percent / 100)
        elif self.discount_amount:
            return min(self.discount_amount, amount)
        return Decimal("0.00")


class Order(models.Model):
    coupon = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL, null=True, blank=True
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "orders_order"
```