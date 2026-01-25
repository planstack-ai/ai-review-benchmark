# Existing Codebase

## Schema

```sql
CREATE TABLE cart (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE cart_item (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES cart(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES product(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE UNIQUE INDEX cart_user_idx ON cart(user_id);
CREATE UNIQUE INDEX cart_item_cart_product_idx ON cart_item(cart_id, product_id);
```

## Models

```python
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from typing import Optional


class CartManager(models.Manager):
    def get_or_create_for_user(self, user: User) -> tuple['Cart', bool]:
        return self.get_or_create(user=user)
    
    def for_user(self, user: User) -> models.QuerySet['Cart']:
        return self.filter(user=user)


class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CartManager()
    
    class Meta:
        db_table = 'cart'
    
    def __str__(self) -> str:
        return f"Cart for {self.user.username}"
    
    @property
    def total_items(self) -> int:
        return self.items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    def clear(self) -> None:
        self.items.all().delete()


class CartItemManager(models.Manager):
    def for_cart(self, cart: Cart) -> models.QuerySet['CartItem']:
        return self.filter(cart=cart)
    
    def for_user_cart(self, user: User) -> models.QuerySet['CartItem']:
        return self.filter(cart__user=user)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CartItemManager()
    
    class Meta:
        db_table = 'cart_item'
        unique_together = ('cart', 'product')
    
    def __str__(self) -> str:
        return f"{self.quantity}x {self.product.name} in {self.cart}"
    
    def clean(self) -> None:
        if self.quantity <= 0:
            raise ValidationError("Quantity must be positive")


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'product'
    
    def __str__(self) -> str:
        return self.name
```