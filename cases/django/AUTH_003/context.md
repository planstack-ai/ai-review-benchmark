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
    deleted_at: Optional[timezone.datetime] = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users_user'
    
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
    
    def soft_delete(self) -> None:
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['deleted_at', 'is_active'])


class OrderQuerySet(models.QuerySet):
    def with_active_users(self):
        return self.select_related('user').filter(
            user__is_active=True,
            user__deleted_at__isnull=True
        )
    
    def for_user(self, user: User):
        return self.filter(user=user)
    
    def completed(self):
        return self.filter(status='completed')


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)
    
    def with_active_users(self):
        return self.get_queryset().with_active_users()


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    user: User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number: str = models.CharField(max_length=50, unique=True)
    total_amount: Decimal = models.DecimalField(max_digits=10, decimal_places=2)
    status: str = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at: timezone.datetime = models.DateTimeField(auto_now_add=True)
    updated_at: timezone.datetime = models.DateTimeField(auto_now=True)
    
    objects = OrderManager()
    
    class Meta:
        db_table = 'orders_order'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    order: Order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name: str = models.CharField(max_length=255)
    quantity: int = models.PositiveIntegerField()
    unit_price: Decimal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'orders_orderitem'
    
    @property
    def total_price(self) -> Decimal:
        return self.quantity * self.unit_price
```