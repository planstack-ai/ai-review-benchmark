# Existing Codebase

## Schema

```sql
CREATE TABLE inventory_product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    price DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE inventory_stockmovement (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES inventory_product(id),
    movement_type VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    reference VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

## Models

```python
from decimal import Decimal
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone
from typing import Dict, List, Optional


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)
    
    def low_stock(self, threshold: int = 10):
        return self.filter(stock_quantity__lte=threshold)
    
    def available_stock(self):
        return self.annotate(
            available=F('stock_quantity') - F('reserved_quantity')
        )


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def bulk_adjust_stock(self, adjustments: Dict[int, int]) -> int:
        """Bulk adjust stock quantities without triggering signals."""
        if not adjustments:
            return 0
        
        product_ids = list(adjustments.keys())
        return self.filter(id__in=product_ids).bulk_update(
            [
                self.model(id=pid, stock_quantity=F('stock_quantity') + qty)
                for pid, qty in adjustments.items()
            ],
            fields=['stock_quantity'],
            batch_size=100
        )


class Product(models.Model):
    MOVEMENT_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJUST', 'Adjustment'),
        ('RESERVE', 'Reserved'),
        ('RELEASE', 'Released'),
    ]
    
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ProductManager()
    
    class Meta:
        db_table = 'inventory_product'
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['is_active', 'stock_quantity']),
        ]
    
    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"
    
    @property
    def available_quantity(self) -> int:
        return max(0, self.stock_quantity - self.reserved_quantity)
    
    def can_fulfill(self, quantity: int) -> bool:
        return self.available_quantity >= quantity


class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=Product.MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inventory_stockmovement'
        indexes = [
            models.Index(fields=['product', 'created_at']),
            models.Index(fields=['movement_type', 'created_at']),
        ]
```