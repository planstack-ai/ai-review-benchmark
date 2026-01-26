# Existing Codebase

## Schema

```sql
-- Products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    product_type VARCHAR(20) NOT NULL CHECK (product_type IN ('simple', 'bundle')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Stock table
CREATE TABLE stock (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Bundle components table
CREATE TABLE bundle_components (
    id SERIAL PRIMARY KEY,
    bundle_id INTEGER REFERENCES products(id),
    component_id INTEGER REFERENCES products(id),
    quantity_required INTEGER NOT NULL DEFAULT 1,
    UNIQUE(bundle_id, component_id)
);
```

## Models

```python
from django.db import models
from django.db.models import F, Min, Q
from typing import Optional


class ProductType(models.TextChoices):
    SIMPLE = 'simple', 'Simple Product'
    BUNDLE = 'bundle', 'Bundle Product'


class StockQuerySet(models.QuerySet):
    def available(self):
        return self.annotate(
            available_quantity=F('quantity') - F('reserved_quantity')
        )
    
    def with_positive_stock(self):
        return self.available().filter(available_quantity__gt=0)


class StockManager(models.Manager):
    def get_queryset(self):
        return StockQuerySet(self.model, using=self._db)
    
    def available(self):
        return self.get_queryset().available()


class Product(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.SIMPLE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
    
    def __str__(self) -> str:
        return f"{self.sku} - {self.name}"
    
    @property
    def is_bundle(self) -> bool:
        return self.product_type == ProductType.BUNDLE


class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='stock')
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = StockManager()
    
    class Meta:
        db_table = 'stock'
    
    @property
    def available_quantity(self) -> int:
        return max(0, self.quantity - self.reserved_quantity)


class BundleComponent(models.Model):
    bundle = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='components'
    )
    component = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='used_in_bundles'
    )
    quantity_required = models.PositiveIntegerField(default=1)
    
    class Meta:
        db_table = 'bundle_components'
        unique_together = ('bundle', 'component')
    
    def __str__(self) -> str:
        return f"{self.bundle.sku} -> {self.component.sku} (x{self.quantity_required})"
```