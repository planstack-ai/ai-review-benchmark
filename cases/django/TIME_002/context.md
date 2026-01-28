# Existing Codebase

## Schema

```sql
CREATE TABLE sales_sale (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE sales_saleitem (
    id BIGINT PRIMARY KEY,
    sale_id BIGINT REFERENCES sales_sale(id),
    product_id BIGINT NOT NULL,
    discount_percentage DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Models

```python
from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from django.db import models
from django.utils import timezone


class SaleQuerySet(models.QuerySet):
    def active(self) -> "SaleQuerySet":
        return self.filter(is_active=True)
    
    def for_date(self, target_date: date) -> "SaleQuerySet":
        return self.filter(
            start_date__lte=target_date,
            end_date__gte=target_date
        )


class SaleManager(models.Manager):
    def get_queryset(self) -> SaleQuerySet:
        return SaleQuerySet(self.model, using=self._db)
    
    def active(self) -> SaleQuerySet:
        return self.get_queryset().active()
    
    def current(self) -> SaleQuerySet:
        today = timezone.now().date()
        return self.active().for_date(today)


class Sale(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = SaleManager()
    
    class Meta:
        db_table = 'sales_sale'
        ordering = ['-start_date']
    
    def __str__(self) -> str:
        return self.name
    
    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days + 1
    
    def get_start_datetime(self, tz: Optional[timezone.tzinfo.BaseTzInfo] = None) -> datetime:
        """Convert start_date to datetime at beginning of day."""
        if tz is None:
            tz = timezone.get_current_timezone()
        return timezone.make_aware(
            datetime.combine(self.start_date, time.min), 
            timezone=tz
        )
    
    def get_end_datetime(self, tz: Optional[timezone.tzinfo.BaseTzInfo] = None) -> datetime:
        """Convert end_date to datetime at end of day."""
        if tz is None:
            tz = timezone.get_current_timezone()
        return timezone.make_aware(
            datetime.combine(self.end_date, time.max),
            timezone=tz
        )


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product_id = models.BigIntegerField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sales_saleitem'
        unique_together = ['sale', 'product_id']
    
    def __str__(self) -> str:
        return f"{self.sale.name} - Product {self.product_id}"
    
    @property
    def discount_decimal(self) -> Decimal:
        return self.discount_percentage / Decimal('100')
```