# Existing Codebase

## Schema

```sql
CREATE TABLE payments_payment (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    payment_method VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE payments_refund (
    id BIGINT PRIMARY KEY,
    payment_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    reason TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    refund_reference VARCHAR(100) UNIQUE,
    processed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payment_id) REFERENCES payments_payment(id)
);
```

## Models

```python
from decimal import Decimal
from django.db import models
from django.utils import timezone
from typing import Optional


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'
    PARTIALLY_REFUNDED = 'partially_refunded', 'Partially Refunded'
    FULLY_REFUNDED = 'fully_refunded', 'Fully Refunded'


class RefundStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'


class PaymentQuerySet(models.QuerySet):
    def completed(self):
        return self.filter(status=PaymentStatus.COMPLETED)
    
    def refundable(self):
        return self.filter(
            status__in=[
                PaymentStatus.COMPLETED,
                PaymentStatus.PARTIALLY_REFUNDED
            ]
        )


class PaymentManager(models.Manager):
    def get_queryset(self):
        return PaymentQuerySet(self.model, using=self._db)
    
    def completed(self):
        return self.get_queryset().completed()
    
    def refundable(self):
        return self.get_queryset().refundable()


class Payment(models.Model):
    order_id = models.BigIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = PaymentManager()
    
    class Meta:
        db_table = 'payments_payment'
    
    def get_total_refunded_amount(self) -> Decimal:
        return self.refunds.filter(
            status=RefundStatus.COMPLETED
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
    
    def get_refundable_amount(self) -> Decimal:
        return self.amount - self.get_total_refunded_amount()
    
    def is_fully_refunded(self) -> bool:
        return self.get_total_refunded_amount() >= self.amount
    
    def is_partially_refunded(self) -> bool:
        refunded = self.get_total_refunded_amount()
        return Decimal('0.00') < refunded < self.amount


class Refund(models.Model):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='refunds'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=RefundStatus.choices,
        default=RefundStatus.PENDING
    )
    refund_reference = models.CharField(max_length=100, unique=True, null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payments_refund'
    
    def mark_as_completed(self, refund_reference: Optional[str] = None) -> None:
        self.status = RefundStatus.COMPLETED
        self.processed_at = timezone.now()
        if refund_reference:
            self.refund_reference = refund_reference
        self.save(update_fields=['status', 'processed_at', 'refund_reference'])
```