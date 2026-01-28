# Existing Codebase

## Schema

```sql
CREATE TABLE inventory_product (
    id BIGINT PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    allow_negative_stock BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory_stocklevel (
    id BIGINT PRIMARY KEY,
    product_id BIGINT REFERENCES inventory_product(id),
    warehouse_id BIGINT REFERENCES inventory_warehouse(id),
    quantity INTEGER DEFAULT 0,
    reserved_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, warehouse_id)
);

CREATE TABLE inventory_stockmovement (
    id BIGINT PRIMARY KEY,
    product_id BIGINT REFERENCES inventory_product(id),
    warehouse_id BIGINT REFERENCES inventory_warehouse(id),
    movement_type VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    reference VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Models

```python
from django.db import models, transaction
from django.core.exceptions import ValidationError
from typing import Optional


class InsufficientStockError(Exception):
    """Raised when attempting to reduce stock below zero for products that don't allow negative stock."""
    pass


class StockMovementType(models.TextChoices):
    INBOUND = "inbound", "Inbound"
    OUTBOUND = "outbound", "Outbound"
    ADJUSTMENT = "adjustment", "Adjustment"
    TRANSFER = "transfer", "Transfer"


class Product(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    allow_negative_stock = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inventory_product"

    def __str__(self) -> str:
        return f"{self.sku} - {self.name}"


class StockLevelManager(models.Manager):
    def get_available_quantity(self, product_id: int, warehouse_id: int) -> int:
        """Returns available quantity (quantity - reserved_quantity)."""
        try:
            stock_level = self.get(product_id=product_id, warehouse_id=warehouse_id)
            return stock_level.quantity - stock_level.reserved_quantity
        except StockLevel.DoesNotExist:
            return 0

    def create_or_get(self, product_id: int, warehouse_id: int) -> tuple["StockLevel", bool]:
        """Creates or gets a stock level record."""
        return self.get_or_create(
            product_id=product_id,
            warehouse_id=warehouse_id,
            defaults={"quantity": 0, "reserved_quantity": 0}
        )


class StockLevel(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey("Warehouse", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = StockLevelManager()

    class Meta:
        db_table = "inventory_stocklevel"
        unique_together = [["product", "warehouse"]]

    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity

    def clean(self) -> None:
        if self.reserved_quantity < 0:
            raise ValidationError("Reserved quantity cannot be negative")


class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey("Warehouse", on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=StockMovementType.choices)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inventory_stockmovement"
        ordering = ["-created_at"]


class Warehouse(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"
```