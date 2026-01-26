# Existing Codebase

## Schema

```python
# migrations/0001_initial.py
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('is_active', models.BooleanField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock_quantity', models.IntegerField()),
                ('is_featured', models.BooleanField()),
                ('created_at', models.DateTimeField()),
            ],
        ),
    ]
```

## Models

```python
from django.db import models
from django.utils import timezone
from decimal import Decimal
from typing import Optional


class TimestampedModel(models.Model):
    """Abstract base model with timestamp fields."""
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class ActiveManager(models.Manager):
    """Manager for active records only."""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class User(TimestampedModel):
    """User model for the application."""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField()
    
    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])


class FeaturedProductManager(models.Manager):
    """Manager for featured products."""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_featured=True, stock_quantity__gt=0)


class Product(models.Model):
    """Product model for the e-commerce system."""
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    is_featured = models.BooleanField()
    created_at = models.DateTimeField()

    objects = models.Manager()
    featured = FeaturedProductManager()

    class Meta:
        db_table = 'products'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    @property
    def is_in_stock(self) -> bool:
        return self.stock_quantity > 0

    def reduce_stock(self, quantity: int) -> bool:
        """Reduce stock quantity if sufficient stock available."""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save(update_fields=['stock_quantity'])
            return True
        return False

    @classmethod
    def get_default_price(cls) -> Decimal:
        """Get default price for new products."""
        return Decimal('0.00')
```