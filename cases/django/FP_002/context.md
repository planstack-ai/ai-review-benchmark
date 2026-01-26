# Existing Codebase

## Schema

```sql
CREATE TABLE users_user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(254) UNIQUE NOT NULL,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    phone_number VARCHAR(20),
    date_of_birth DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE products_product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Models

```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import re


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class User(TimestampedModel):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(
        max_length=20, 
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')]
    )
    date_of_birth = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    objects = models.Manager()
    active = ActiveManager()
    
    def clean(self):
        super().clean()
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError({'date_of_birth': 'Date of birth cannot be in the future.'})
        
        if self.email:
            self.email = self.email.lower()
    
    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
    
    def __str__(self) -> str:
        return self.username


class Product(TimestampedModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    objects = models.Manager()
    active = ActiveManager()
    
    def clean(self):
        super().clean()
        if self.name:
            self.name = self.name.strip()
        
        if self.slug and not re.match(r'^[-a-zA-Z0-9_]+$', self.slug):
            raise ValidationError({'slug': 'Slug can only contain letters, numbers, hyphens, and underscores.'})
    
    def is_in_stock(self) -> bool:
        return self.stock_quantity > 0
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        ordering = ['name']
```