# Existing Codebase

## Schema

```sql
CREATE TABLE inventory_product (
    id BIGINT PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE inventory_stock (
    id BIGINT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES inventory_product(id)
);

CREATE TABLE cart_cartitem (
    id BIGINT PRIMARY KEY,
    cart_id VARCHAR(255) NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES inventory_product(id)
);
```

## Models

```python
from decimal import Decimal
from django.db import models
from django.db.models import F, Q
from typing import Dict, List


class StockManager(models.Manager):
    def get_available_quantities(self, product_ids: List[int]) -> Dict[int, int]:
        """Returns available stock quantities for given product IDs."""
        return dict(
            self.filter(product_id__in=product_ids)
            .annotate(available=F('quantity') - F('reserved_quantity'))
            .values_list('product_id', 'available')
        )
    
    def bulk_reserve(self, reservations: Dict[int, int]) -> bool:
        """Atomically reserves stock for multiple products."""
        with transaction.atomic():
            for product_id, qty in reservations.items():
                updated = self.filter(
                    product_id=product_id,
                    quantity__gte=F('reserved_quantity') + qty
                ).update(reserved_quantity=F('reserved_quantity') + qty)
                if not updated:
                    return False
            return True


class Product(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_product'


class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    objects = StockManager()

    class Meta:
        db_table = 'inventory_stock'

    @property
    def available_quantity(self) -> int:
        return max(0, self.quantity - self.reserved_quantity)


class CartItemQuerySet(models.QuerySet):
    def for_cart(self, cart_id: str):
        return self.filter(cart_id=cart_id)
    
    def with_products(self):
        return self.select_related('product')


class CartItem(models.Model):
    cart_id = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CartItemQuerySet.as_manager()

    class Meta:
        db_table = 'cart_cartitem'
        unique_together = ['cart_id', 'product']

    @property
    def total_price(self) -> Decimal:
        return self.product.price * self.quantity
```