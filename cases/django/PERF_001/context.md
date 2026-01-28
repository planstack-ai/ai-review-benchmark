# Existing Codebase

## Schema

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_email VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE
);
```

## Models

```python
from decimal import Decimal
from django.db import models
from django.db.models import QuerySet, Sum, F
from typing import Optional


class CategoryQuerySet(QuerySet):
    def active(self) -> QuerySet:
        return self.filter(is_active=True)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    
    objects = CategoryQuerySet.as_manager()
    
    class Meta:
        verbose_name_plural = "categories"
    
    def __str__(self) -> str:
        return self.name


class ProductQuerySet(QuerySet):
    def available(self) -> QuerySet:
        return self.filter(is_available=True)
    
    def with_category(self) -> QuerySet:
        return self.select_related('category')


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = ProductQuerySet.as_manager()
    
    def __str__(self) -> str:
        return self.name


class OrderQuerySet(QuerySet):
    def pending(self) -> QuerySet:
        return self.filter(status='pending')
    
    def completed(self) -> QuerySet:
        return self.filter(status='completed')
    
    def with_totals(self) -> QuerySet:
        return self.annotate(
            calculated_total=Sum(F('items__quantity') * F('items__unit_price'))
        )


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer_email = models.EmailField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = OrderQuerySet.as_manager()
    
    def calculate_total(self) -> Decimal:
        return sum(item.get_total_price() for item in self.items.all())
    
    def __str__(self) -> str:
        return f"Order #{self.id} - {self.customer_email}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def get_total_price(self) -> Decimal:
        return self.quantity * self.unit_price
    
    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.quantity}x {self.product.name}"
```