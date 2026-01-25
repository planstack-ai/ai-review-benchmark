# Existing Codebase

## Schema

```sql
CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE products_product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    member_price DECIMAL(10, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE orders_order (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    total_amount DECIMAL(10, 2) NOT NULL,
    is_member_pricing BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Models

```python
from decimal import Decimal
from typing import Optional

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet


class ProductQuerySet(QuerySet):
    def active(self) -> QuerySet:
        return self.filter(is_active=True)
    
    def with_member_pricing(self) -> QuerySet:
        return self.filter(member_price__isnull=False)


class ProductManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        return ProductQuerySet(self.model, using=self._db)
    
    def active(self) -> QuerySet:
        return self.get_queryset().active()


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    member_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = ProductManager()
    
    def has_member_pricing(self) -> bool:
        return self.member_price is not None
    
    def get_savings_amount(self) -> Optional[Decimal]:
        if self.has_member_pricing():
            return self.base_price - self.member_price
        return None
    
    def get_savings_percentage(self) -> Optional[int]:
        savings = self.get_savings_amount()
        if savings and self.base_price > 0:
            return int((savings / self.base_price) * 100)
        return None


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_member_pricing = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def is_guest_order(self) -> bool:
        return self.user is None
    
    @property
    def is_member_order(self) -> bool:
        return self.user is not None and self.user.is_active


# Constants
GUEST_USER_SESSION_KEY = 'guest_user_id'
MEMBER_PRICING_ENABLED = True
```