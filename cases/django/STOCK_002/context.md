# Existing Codebase

## Schema

```sql
CREATE TABLE inventory_product (
    id BIGINT PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE inventory_stocklevel (
    id BIGINT PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES inventory_product(id),
    warehouse_code VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(product_id, warehouse_code)
);

CREATE INDEX idx_stocklevel_product_warehouse ON inventory_stocklevel(product_id, warehouse_code);
```

## Models

```python
from django.db import models, transaction
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


class StockLevelQuerySet(models.QuerySet):
    def for_warehouse(self, warehouse_code: str):
        return self.filter(warehouse_code=warehouse_code)
    
    def available_stock(self):
        return self.annotate(
            available=models.F('quantity') - models.F('reserved_quantity')
        )
    
    def with_sufficient_stock(self, required_quantity: int):
        return self.available_stock().filter(
            available__gte=required_quantity
        )


class StockLevelManager(models.Manager):
    def get_queryset(self):
        return StockLevelQuerySet(self.model, using=self._db)
    
    def for_warehouse(self, warehouse_code: str):
        return self.get_queryset().for_warehouse(warehouse_code)
    
    def available_stock(self):
        return self.get_queryset().available_stock()


class StockLevel(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='stock_levels'
    )
    warehouse_code = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = StockLevelManager()

    class Meta:
        db_table = 'inventory_stocklevel'
        unique_together = [['product', 'warehouse_code']]
        indexes = [
            models.Index(fields=['product', 'warehouse_code']),
        ]

    @property
    def available_quantity(self) -> int:
        return max(0, self.quantity - self.reserved_quantity)

    def clean(self):
        if self.reserved_quantity > self.quantity:
            raise ValidationError(
                "Reserved quantity cannot exceed total quantity"
            )

    def __str__(self) -> str:
        return f"{self.product.sku} @ {self.warehouse_code}: {self.available_quantity}"


class InsufficientStockError(Exception):
    def __init__(self, product_sku: str, warehouse_code: str, 
                 requested: int, available: int):
        self.product_sku = product_sku
        self.warehouse_code = warehouse_code
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient stock for {product_sku} in {warehouse_code}: "
            f"requested {requested}, available {available}"
        )
```