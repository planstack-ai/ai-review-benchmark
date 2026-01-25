# Existing Codebase

## Schema

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    tax_rate DECIMAL(5,4) DEFAULT 0.0000,
    discount_percentage DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Models

```python
from decimal import Decimal, ROUND_HALF_UP
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from typing import Optional


class PriceManager(models.Manager):
    def with_calculated_prices(self):
        return self.select_related().annotate(
            calculated_total=models.F('base_price') * models.F('quantity')
        )


class Product(models.Model):
    name = models.CharField(max_length=255)
    base_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=Decimal('0.0000'),
        validators=[
            MinValueValidator(Decimal('0.0000')),
            MaxValueValidator(Decimal('1.0000'))
        ]
    )
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'

    def get_tax_amount(self, price: Decimal) -> Decimal:
        return (price * self.tax_rate).quantize(
            Decimal('0.01'), 
            rounding=ROUND_HALF_UP
        )

    def apply_discount(self, price: Decimal) -> Decimal:
        discount_multiplier = Decimal('1.00') - (self.discount_percentage / Decimal('100'))
        return (price * discount_multiplier).quantize(
            Decimal('0.01'), 
            rounding=ROUND_HALF_UP
        )


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PriceManager()

    class Meta:
        db_table = 'order_items'

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.product.base_price
        super().save(*args, **kwargs)


# Constants
CURRENCY_PRECISION = Decimal('0.01')
DEFAULT_ROUNDING = ROUND_HALF_UP
MAX_PRICE_DIGITS = 10
PRICE_DECIMAL_PLACES = 2
```