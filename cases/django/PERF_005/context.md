# Existing Codebase

## Schema

```sql
-- Users table with indexes
CREATE TABLE users_user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(254) UNIQUE NOT NULL,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(30),
    last_name VARCHAR(30),
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users_user(email);
CREATE INDEX idx_users_username ON users_user(username);
CREATE INDEX idx_users_active_joined ON users_user(is_active, date_joined);
CREATE INDEX idx_users_last_login ON users_user(last_login);

-- Products table with indexes
CREATE TABLE products_product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    category_id INTEGER REFERENCES categories_category(id),
    price DECIMAL(10,2),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_products_slug ON products_product(slug);
CREATE INDEX idx_products_category ON products_product(category_id);
CREATE INDEX idx_products_available_price ON products_product(is_available, price);
CREATE INDEX idx_products_created_at ON products_product(created_at);
```

## Models

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from typing import Optional


class UserManager(models.Manager):
    def active_users(self):
        return self.filter(is_active=True)
    
    def recent_logins(self, days: int = 30):
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(last_login__gte=cutoff)


class User(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)
    date_joined = models.DateTimeField(default=timezone.now, db_index=True)
    last_login = models.DateTimeField(null=True, blank=True, db_index=True)
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users_user'
        indexes = [
            models.Index(fields=['is_active', 'date_joined']),
        ]


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.filter(is_available=True)
    
    def by_category(self, category_id: int):
        return self.filter(category_id=category_id)
    
    def price_range(self, min_price: Optional[float] = None, max_price: Optional[float] = None):
        qs = self
        if min_price is not None:
            qs = qs.filter(price__gte=min_price)
        if max_price is not None:
            qs = qs.filter(price__lte=max_price)
        return qs


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)
    
    def available(self):
        return self.get_queryset().available()
    
    def by_slug(self, slug: str):
        return self.get_queryset().filter(slug=slug)


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        db_table = 'categories_category'


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ProductManager()
    
    class Meta:
        db_table = 'products_product'
        indexes = [
            models.Index(fields=['is_available', 'price']),
        ]
```