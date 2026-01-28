# Existing Codebase

## Schema

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    discount_rate DECIMAL(5,4) DEFAULT 0.0000,
    tax_rate DECIMAL(5,4) DEFAULT 0.0000
);

CREATE TABLE pricing_tiers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    min_quantity INTEGER NOT NULL,
    discount_percentage DECIMAL(5,2) NOT NULL
);

CREATE TABLE seasonal_adjustments (
    id SERIAL PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    adjustment_factor DECIMAL(5,4) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

## Models

```python
from decimal import Decimal
from django.db import models
from django.utils import timezone
from typing import Optional


class PricingTierManager(models.Manager):
    def get_tier_for_quantity(self, quantity: int) -> Optional['PricingTier']:
        return self.filter(
            min_quantity__lte=quantity
        ).order_by('-min_quantity').first()


class SeasonalAdjustmentManager(models.Manager):
    def get_current_adjustment(self) -> Optional['SeasonalAdjustment']:
        today = timezone.now().date()
        return self.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_active=True
        ).first()


class Category(models.Model):
    name = models.CharField(max_length=100)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0000'))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0000'))

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    @property
    def category_discount_rate(self) -> Decimal:
        return self.category.discount_rate

    @property
    def category_tax_rate(self) -> Decimal:
        return self.category.tax_rate


class PricingTier(models.Model):
    name = models.CharField(max_length=50)
    min_quantity = models.PositiveIntegerField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    objects = PricingTierManager()

    class Meta:
        ordering = ['min_quantity']

    def __str__(self) -> str:
        return f"{self.name} ({self.min_quantity}+ items)"

    @property
    def discount_factor(self) -> Decimal:
        return Decimal('1.0') - (self.discount_percentage / Decimal('100'))


class SeasonalAdjustment(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    adjustment_factor = models.DecimalField(max_digits=5, decimal_places=4)
    is_active = models.BooleanField(default=True)

    objects = SeasonalAdjustmentManager()

    def __str__(self) -> str:
        return f"Adjustment {self.adjustment_factor} ({self.start_date} - {self.end_date})"

    @property
    def is_current(self) -> bool:
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date and self.is_active
```