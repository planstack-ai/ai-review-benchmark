# Existing Codebase

## Schema

```sql
CREATE TABLE inventory_product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE inventory_stockmovement (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES inventory_product(id),
    movement_type VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_product_sku ON inventory_product(sku);
CREATE INDEX idx_product_active ON inventory_product(is_active);
CREATE INDEX idx_stockmovement_product ON inventory_stockmovement(product_id);
```

## Models

```python
from decimal import Decimal
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from typing import Dict, List


class ProductQuerySet(QuerySet):
    def active(self) -> QuerySet:
        return self.filter(is_active=True)
    
    def by_sku_list(self, skus: List[str]) -> QuerySet:
        return self.filter(sku__in=skus)
    
    def low_stock(self, threshold: int = 10) -> QuerySet:
        return self.filter(stock_quantity__lte=threshold)


class ProductManager(models.Manager):
    def get_queryset(self) -> ProductQuerySet:
        return ProductQuerySet(self.model, using=self._db)
    
    def active(self) -> QuerySet:
        return self.get_queryset().active()
    
    def bulk_update_stock(self, stock_updates: Dict[str, int]) -> int:
        """Update stock quantities for multiple products by SKU."""
        products = list(self.by_sku_list(list(stock_updates.keys())))
        
        for product in products:
            if product.sku in stock_updates:
                product.stock_quantity = stock_updates[product.sku]
                product.updated_at = timezone.now()
        
        return self.bulk_update(
            products, 
            ['stock_quantity', 'updated_at'],
            batch_size=100
        )


class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ProductManager()
    
    class Meta:
        db_table = 'inventory_product'
        ordering = ['name']
    
    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"
    
    def is_low_stock(self, threshold: int = 10) -> bool:
        return self.stock_quantity <= threshold
    
    def adjust_stock(self, quantity: int, reason: str = "") -> None:
        """Adjust stock and create movement record."""
        self.stock_quantity += quantity
        self.save(update_fields=['stock_quantity', 'updated_at'])
        
        StockMovement.objects.create(
            product=self,
            movement_type='adjustment',
            quantity=quantity,
            reason=reason
        )


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inventory_stockmovement'
        ordering = ['-created_at']
```