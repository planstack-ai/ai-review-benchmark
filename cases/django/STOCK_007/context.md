# Existing Codebase

## Schema

```sql
CREATE TABLE inventory_product (
    id BIGINT PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE orders_order (
    id BIGINT PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE orders_orderitem (
    id BIGINT PRIMARY KEY,
    order_id BIGINT REFERENCES orders_order(id),
    product_id BIGINT REFERENCES inventory_product(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE inventory_stockmovement (
    id BIGINT PRIMARY KEY,
    product_id BIGINT REFERENCES inventory_product(id),
    movement_type VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    reference_type VARCHAR(50),
    reference_id BIGINT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

## Models

```python
from django.db import models, transaction
from django.utils import timezone
from typing import Optional


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'


class MovementType(models.TextChoices):
    RESERVATION = 'reservation', 'Stock Reservation'
    RELEASE = 'release', 'Stock Release'
    SALE = 'sale', 'Sale'
    RETURN = 'return', 'Return'
    ADJUSTMENT = 'adjustment', 'Adjustment'


class Product(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    stock_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.sku} - {self.name}"

    def has_sufficient_stock(self, quantity: int) -> bool:
        return self.stock_quantity >= quantity

    @transaction.atomic
    def adjust_stock(self, quantity: int, movement_type: str, 
                    reference_type: Optional[str] = None, 
                    reference_id: Optional[int] = None) -> 'StockMovement':
        self.stock_quantity += quantity
        self.save(update_fields=['stock_quantity', 'updated_at'])
        
        return StockMovement.objects.create(
            product=self,
            movement_type=movement_type,
            quantity=quantity,
            reference_type=reference_type,
            reference_id=reference_id
        )


class Order(models.Model):
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, 
                             default=OrderStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Order {self.order_number}"

    @property
    def is_cancelled(self) -> bool:
        return self.status == OrderStatus.CANCELLED

    def get_reserved_items(self):
        return self.items.select_related('product')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['order', 'product']

    def __str__(self) -> str:
        return f"{self.quantity}x {self.product.sku} in {self.order.order_number}"


class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                               related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    quantity = models.IntegerField()
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.movement_type}: {self.quantity} units of {self.product.sku}"

    @classmethod
    def has_release_movement(cls, reference_type: str, reference_id: int) -> bool:
        return cls.objects.filter(
            movement_type=MovementType.RELEASE,
            reference_type=reference_type,
            reference_id=reference_id
        ).exists()
```