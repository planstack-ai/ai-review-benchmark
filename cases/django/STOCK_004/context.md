# Existing Codebase

## Schema

```sql
CREATE TABLE inventory_product (
    id BIGINT PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE inventory_stocklocation (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE inventory_stockrecord (
    id BIGINT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    location_id BIGINT NOT NULL,
    quantity_on_hand INTEGER DEFAULT 0,
    quantity_reserved INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES inventory_product(id),
    FOREIGN KEY (location_id) REFERENCES inventory_stocklocation(id),
    UNIQUE(product_id, location_id)
);
```

## Models

```python
from django.db import models
from django.core.exceptions import ValidationError
from typing import Optional


class Product(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_product'

    def __str__(self) -> str:
        return f"{self.sku} - {self.name}"


class StockLocation(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'inventory_stocklocation'

    def __str__(self) -> str:
        return self.name


class StockRecordQuerySet(models.QuerySet):
    def with_availability(self):
        return self.annotate(
            available_quantity=models.F('quantity_on_hand') - models.F('quantity_reserved')
        )

    def for_product(self, product):
        return self.filter(product=product)

    def active_locations(self):
        return self.filter(location__is_active=True)


class StockRecordManager(models.Manager):
    def get_queryset(self):
        return StockRecordQuerySet(self.model, using=self._db)

    def with_availability(self):
        return self.get_queryset().with_availability()

    def for_product(self, product):
        return self.get_queryset().for_product(product)


class StockRecord(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(StockLocation, on_delete=models.CASCADE)
    quantity_on_hand = models.IntegerField(default=0)
    quantity_reserved = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = StockRecordManager()

    class Meta:
        db_table = 'inventory_stockrecord'
        unique_together = [['product', 'location']]

    def clean(self):
        if self.quantity_on_hand < 0:
            raise ValidationError("Quantity on hand cannot be negative")
        if self.quantity_reserved < 0:
            raise ValidationError("Quantity reserved cannot be negative")
        if self.quantity_reserved > self.quantity_on_hand:
            raise ValidationError("Reserved quantity cannot exceed quantity on hand")

    @property
    def available_quantity(self) -> int:
        return self.quantity_on_hand - self.quantity_reserved

    def can_reserve(self, quantity: int) -> bool:
        return self.available_quantity >= quantity

    def __str__(self) -> str:
        return f"{self.product.sku} @ {self.location.code}: {self.quantity_on_hand} on hand, {self.quantity_reserved} reserved"
```