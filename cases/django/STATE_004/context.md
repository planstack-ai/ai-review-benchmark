# Existing Codebase

## Schema

```sql
CREATE TABLE orders_order (
    id BIGINT PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id BIGINT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE payments_payment (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(100) UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    processed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders_order(id)
);
```

## Models

```python
from decimal import Decimal
from django.db import models
from django.utils import timezone
from typing import Optional


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    REFUNDED = 'refunded', 'Refunded'


class Order(models.Model):
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders_order'

    def __str__(self) -> str:
        return f"Order {self.order_number}"

    def get_total_paid_amount(self) -> Decimal:
        return self.payments.filter(
            status=PaymentStatus.COMPLETED
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

    def is_fully_paid(self) -> bool:
        return self.get_total_paid_amount() >= self.total_amount

    def has_successful_payment(self) -> bool:
        return self.payments.filter(status=PaymentStatus.COMPLETED).exists()


class PaymentQuerySet(models.QuerySet):
    def completed(self):
        return self.filter(status=PaymentStatus.COMPLETED)

    def for_order(self, order_id: int):
        return self.filter(order_id=order_id)

    def pending_or_processing(self):
        return self.filter(status__in=[PaymentStatus.PENDING, PaymentStatus.PROCESSING])


class PaymentManager(models.Manager):
    def get_queryset(self):
        return PaymentQuerySet(self.model, using=self._db)

    def completed(self):
        return self.get_queryset().completed()

    def for_order(self, order_id: int):
        return self.get_queryset().for_order(order_id)


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PaymentManager()

    class Meta:
        db_table = 'payments_payment'

    def __str__(self) -> str:
        return f"Payment {self.id} for {self.order.order_number}"

    def mark_as_completed(self, transaction_id: Optional[str] = None) -> None:
        self.status = PaymentStatus.COMPLETED
        self.processed_at = timezone.now()
        if transaction_id:
            self.transaction_id = transaction_id
        self.save(update_fields=['status', 'processed_at', 'transaction_id', 'updated_at'])
```