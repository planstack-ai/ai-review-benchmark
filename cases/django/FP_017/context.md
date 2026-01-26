# Existing Codebase

## Schema

```sql
CREATE TABLE products_product (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    category_id BIGINT REFERENCES products_category(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_products_product_category ON products_product(category_id);
CREATE INDEX idx_products_product_sku ON products_product(sku);
```

## Models

```python
from decimal import Decimal
from typing import Any, Dict, List, Optional
from django.db import models, transaction
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name


class ProductQuerySet(models.QuerySet):
    def active(self) -> "ProductQuerySet":
        return self.filter(is_active=True)
    
    def by_category(self, category: Category) -> "ProductQuerySet":
        return self.filter(category=category)
    
    def price_range(self, min_price: Decimal, max_price: Decimal) -> "ProductQuerySet":
        return self.filter(price__gte=min_price, price__lte=max_price)


class ProductManager(models.Manager):
    def get_queryset(self) -> ProductQuerySet:
        return ProductQuerySet(self.model, using=self._db)
    
    def active(self) -> ProductQuerySet:
        return self.get_queryset().active()
    
    def create_product(self, name: str, sku: str, price: Decimal, 
                      category: Category, **kwargs) -> "Product":
        return self.create(
            name=name,
            sku=sku,
            price=price,
            category=category,
            **kwargs
        )


class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ProductManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['sku']),
        ]
    
    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"
    
    def clean(self) -> None:
        if self.price <= 0:
            raise ValueError("Price must be positive")
    
    @property
    def display_price(self) -> str:
        return f"${self.price:.2f}"


class ProductImportLog(models.Model):
    filename = models.CharField(max_length=255)
    total_records = models.PositiveIntegerField()
    successful_imports = models.PositiveIntegerField(default=0)
    failed_imports = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    def mark_completed(self) -> None:
        self.completed_at = timezone.now()
        self.save(update_fields=['completed_at'])
    
    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None
    
    @property
    def success_rate(self) -> float:
        if self.total_records == 0:
            return 0.0
        return (self.successful_imports / self.total_records) * 100
```