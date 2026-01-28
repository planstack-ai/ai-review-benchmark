# Existing Codebase

## Schema

```sql
-- Products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Order items table
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL
);
```

## Models

```python
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from typing import Optional


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class Category(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "categories"


class ProductManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)
    
    def by_category(self, category_slug: str):
        return self.active().filter(category__slug=category_slug)


class Product(TimestampedModel):
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    
    objects = ProductManager()
    
    def __str__(self) -> str:
        return f"{self.sku} - {self.name}"
    
    @property
    def display_price(self) -> str:
        return f"${self.price:.2f}"


class OrderQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status='pending')
    
    def completed(self):
        return self.filter(status='completed')
    
    def for_customer(self, customer_id: int):
        return self.filter(customer_id=customer_id)


class Order(TimestampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    customer_id = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    objects = OrderQuerySet.as_manager()
    
    def __str__(self) -> str:
        return f"Order {self.order_number}"
    
    def calculate_total(self) -> Decimal:
        return sum(item.total_price for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ['order', 'product']
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.quantity}x {self.product.name}"
```