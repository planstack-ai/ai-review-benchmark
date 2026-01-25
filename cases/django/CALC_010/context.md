# Existing Codebase

## Schema

```sql
CREATE TABLE orders_order (
    id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE orders_orderitem (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders_order(id),
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_orderitem_order_id ON orders_orderitem(order_id);
```

## Models

```python
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'


class BulkOrderManager(models.Manager):
    def get_queryset(self) -> 'QuerySet[Order]':
        return super().get_queryset().filter(
            orderitem__quantity__gte=100
        ).distinct()


class Order(models.Model):
    customer_id = models.BigIntegerField()
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = models.Manager()
    bulk_orders = BulkOrderManager()
    
    class Meta:
        db_table = 'orders_order'
    
    def get_item_count(self) -> int:
        return self.orderitem_set.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    def is_bulk_order(self) -> bool:
        return self.orderitem_set.filter(quantity__gte=100).exists()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.BigIntegerField()
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'orders_orderitem'
    
    @property
    def line_total(self) -> Decimal:
        return self.quantity * self.unit_price
    
    def __str__(self) -> str:
        return f"Order {self.order_id} - Product {self.product_id} x{self.quantity}"


# Constants
MAX_SAFE_INTEGER = 2**53 - 1
BULK_ORDER_THRESHOLD = 100
DECIMAL_PRECISION = 2
```