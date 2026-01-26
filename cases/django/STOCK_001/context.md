# Existing Codebase

## Schema

```sql
-- inventory_product table
CREATE TABLE inventory_product (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    total_stock INTEGER NOT NULL DEFAULT 0,
    reserved_stock INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- inventory_stockreservation table
CREATE TABLE inventory_stockreservation (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES inventory_product(id),
    session_key VARCHAR(40),
    user_id INTEGER,
    quantity INTEGER NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- orders_cart table
CREATE TABLE orders_cart (
    id SERIAL PRIMARY KEY,
    session_key VARCHAR(40),
    user_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- orders_cartitem table
CREATE TABLE orders_cartitem (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER REFERENCES orders_cart(id),
    product_id INTEGER REFERENCES inventory_product(id),
    quantity INTEGER NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Models

```python
from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from typing import Optional

User = get_user_model()


class ProductQuerySet(models.QuerySet):
    def with_available_stock(self):
        return self.annotate(
            available_stock=models.F('total_stock') - models.F('reserved_stock')
        )
    
    def in_stock(self):
        return self.with_available_stock().filter(available_stock__gt=0)


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)
    
    def with_available_stock(self):
        return self.get_queryset().with_available_stock()
    
    def in_stock(self):
        return self.get_queryset().in_stock()


class Product(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    total_stock = models.PositiveIntegerField(default=0)
    reserved_stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ProductManager()
    
    class Meta:
        db_table = 'inventory_product'
    
    @property
    def available_stock(self) -> int:
        return max(0, self.total_stock - self.reserved_stock)
    
    def has_stock(self, quantity: int = 1) -> bool:
        return self.available_stock >= quantity


class StockReservationQuerySet(models.QuerySet):
    def active(self):
        return self.filter(expires_at__gt=timezone.now())
    
    def expired(self):
        return self.filter(expires_at__lte=timezone.now())
    
    def for_session(self, session_key: str):
        return self.filter(session_key=session_key)
    
    def for_user(self, user: User):
        return self.filter(user=user)


class StockReservation(models.Model):
    RESERVATION_DURATION = timedelta(minutes=15)
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = StockReservationQuerySet.as_manager()
    
    class Meta:
        db_table = 'inventory_stockreservation'
        indexes = [
            models.Index(fields=['expires_at']),
            models.Index(fields=['session_key']),
            models.Index(fields=['user']),
        ]


class Cart(models.Model):
    session_key = models.CharField(max_length=40, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders_cart'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'orders_cartitem'
        unique_together = ['cart', 'product']
```