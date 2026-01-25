# Existing Codebase

## Schema

```sql
CREATE TABLE products_product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category_id INTEGER REFERENCES products_category(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254),
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE products_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL
);
```

## Models

```python
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from typing import Optional


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser."""
    
    @property
    def is_admin(self) -> bool:
        return self.is_staff or self.is_superuser
    
    def has_product_management_permission(self) -> bool:
        return self.is_admin and self.has_perm('products.change_product')


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "categories"
    
    def __str__(self) -> str:
        return self.name


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)
    
    def by_category(self, category_slug: str):
        return self.filter(category__slug=category_slug)
    
    def price_range(self, min_price: Decimal, max_price: Decimal):
        return self.filter(price__gte=min_price, price__lte=max_price)


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        related_name='products'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    objects = ProductManager()
    
    class Meta:
        permissions = [
            ('change_product_price', 'Can change product price'),
        ]
    
    def __str__(self) -> str:
        return self.name
    
    def get_absolute_url(self) -> str:
        return reverse('products:detail', kwargs={'pk': self.pk})
    
    def update_price(self, new_price: Decimal, user: Optional[User] = None) -> bool:
        """Update product price with validation."""
        if new_price <= 0:
            return False
        self.price = new_price
        self.save(update_fields=['price', 'updated_at'])
        return True
```