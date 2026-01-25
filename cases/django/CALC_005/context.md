# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    line_total DECIMAL(10, 2) NOT NULL
);
```

## Models

```python
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from typing import Optional


class TaxConfiguration(models.Model):
    """Global tax configuration settings."""
    
    name = models.CharField(max_length=100, unique=True)
    rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0000'))]
    )
    is_active = models.BooleanField(default=True)
    effective_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-effective_date']
    
    def __str__(self) -> str:
        return f"{self.name} ({self.rate * 100}%)"


class OrderManager(models.Manager):
    def pending(self):
        return self.filter(status='pending')
    
    def completed(self):
        return self.filter(status='completed')


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer_id = models.IntegerField()
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    tax_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderManager()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Order #{self.id} - ${self.total_amount}"
    
    def get_items_total(self) -> Decimal:
        return sum(item.line_total for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"Item {self.product_id} x{self.quantity}"
```