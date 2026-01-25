# Existing Codebase

## Schema

```sql
CREATE TABLE accounts_user (
    id BIGINT PRIMARY KEY,
    email VARCHAR(254) UNIQUE NOT NULL,
    is_member BOOLEAN DEFAULT FALSE,
    membership_tier VARCHAR(20) DEFAULT 'basic',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products_product (
    id BIGINT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    category_id BIGINT
);

CREATE TABLE orders_order (
    id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES accounts_user(id),
    total_amount DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Models

```python
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from typing import Optional


class User(AbstractUser):
    is_member = models.BooleanField(default=False)
    membership_tier = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic'),
            ('premium', 'Premium'),
            ('vip', 'VIP'),
        ],
        default='basic'
    )
    
    @property
    def eligible_for_discount(self) -> bool:
        return self.is_member


class Product(models.Model):
    name = models.CharField(max_length=200)
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = 'categories'


class OrderManager(models.Manager):
    def for_user(self, user: User):
        return self.filter(user=user)
    
    def with_discounts(self):
        return self.filter(discount_amount__gt=0)


class Order(models.Model):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = OrderManager()
    
    @property
    def final_amount(self) -> Decimal:
        return self.total_amount - self.discount_amount
    
    def __str__(self) -> str:
        return f"Order #{self.id} - {self.user.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity
```