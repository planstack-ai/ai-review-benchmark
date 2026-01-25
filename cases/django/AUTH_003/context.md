# Existing Codebase

## Schema

```sql
CREATE TABLE users_user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(254) UNIQUE NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);

CREATE TABLE orders_order (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_user(id),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    total_amount DECIMAL(10,2),
    status VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE orders_orderitem (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders_order(id),
    product_name VARCHAR(255),
    quantity INTEGER,
    unit_price DECIMAL(10,2)
);
```

## Models

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from typing import Optional
from decimal import Decimal


class UserManager(models.Manager):
    def active(self):
        return self.filter(is_active=True, deleted_at__isnull=True)
    
    def deleted(self):
        return self.filter(deleted_at__isnull=False)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def soft_delete(self) -> None:
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['deleted_at', 'is_active'])
    
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class OrderQuerySet(models.QuerySet):
    def with_user_data(self):
        return self.select_related('user')
    
    def for_active_users(self):
        return self.filter(user__is_active=True, user__deleted_at__isnull=True)
    
    def completed(self):
        return self.filter(status='completed')
    
    def pending(self):
        return self.filter(status='pending')


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)
    
    def with_user_data(self):
        return self.get_queryset().with_user_data()
    
    def for_active_users(self):
        return self.get_queryset().for_active_users()


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderManager()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Order {self.order_number}"
    
    @property
    def customer_email(self) -> Optional[str]:
        return self.user.email if self.user else None


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def total_price(self) -> Decimal:
        return self.quantity * self.unit_price
```