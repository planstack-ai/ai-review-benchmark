# Existing Codebase

## Schema

```sql
-- inventory_item table
CREATE TABLE inventory_item (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    warehouse_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    last_warehouse_sync TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- warehouse table
CREATE TABLE warehouse (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sync_delay_minutes INTEGER NOT NULL DEFAULT 15,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
```

## Models

```python
from datetime import datetime, timedelta
from typing import Optional

from django.db import models
from django.utils import timezone


class WarehouseManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)


class Warehouse(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    sync_delay_minutes = models.PositiveIntegerField(default=15)
    is_active = models.BooleanField(default=True)

    objects = WarehouseManager()

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    @property
    def sync_delay(self) -> timedelta:
        return timedelta(minutes=self.sync_delay_minutes)


class InventoryItemQuerySet(models.QuerySet):
    def with_available_quantity(self):
        return self.annotate(
            available_quantity=models.F('quantity') - models.F('reserved_quantity')
        )

    def in_stock(self):
        return self.with_available_quantity().filter(available_quantity__gt=0)

    def for_warehouse(self, warehouse_id: int):
        return self.filter(warehouse_id=warehouse_id)


class InventoryItemManager(models.Manager):
    def get_queryset(self):
        return InventoryItemQuerySet(self.model, using=self._db)

    def with_available_quantity(self):
        return self.get_queryset().with_available_quantity()

    def in_stock(self):
        return self.get_queryset().in_stock()

    def for_warehouse(self, warehouse_id: int):
        return self.get_queryset().for_warehouse(warehouse_id)


class InventoryItem(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE,
        related_name='inventory_items'
    )
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    last_warehouse_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = InventoryItemManager()

    class Meta:
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['warehouse', 'sku']),
            models.Index(fields=['last_warehouse_sync']),
        ]

    def __str__(self) -> str:
        return f"{self.sku} - {self.name}"

    @property
    def available_quantity(self) -> int:
        return max(0, self.quantity - self.reserved_quantity)

    def is_in_stock(self) -> bool:
        return self.available_quantity > 0

    def get_sync_cutoff_time(self) -> Optional[datetime]:
        if not self.last_warehouse_sync:
            return None
        return self.last_warehouse_sync + self.warehouse.sync_delay
```