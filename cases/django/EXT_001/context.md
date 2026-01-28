# Existing Codebase

## Schema

```sql
CREATE TABLE payments_payment (
    id BIGINT PRIMARY KEY,
    order_id VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    gateway_transaction_id VARCHAR(255),
    gateway_response TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    timeout_count INTEGER NOT NULL DEFAULT 0,
    last_timeout_at TIMESTAMP
);

CREATE INDEX idx_payments_status ON payments_payment(status);
CREATE INDEX idx_payments_order_id ON payments_payment(order_id);
```

## Models

```python
from decimal import Decimal
from django.db import models
from django.utils import timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    TIMEOUT = 'timeout', 'Timeout'
    CANCELLED = 'cancelled', 'Cancelled'


class PaymentQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status=PaymentStatus.PENDING)
    
    def processing(self):
        return self.filter(status=PaymentStatus.PROCESSING)
    
    def with_timeouts(self):
        return self.filter(timeout_count__gt=0)


class PaymentManager(models.Manager):
    def get_queryset(self):
        return PaymentQuerySet(self.model, using=self._db)
    
    def pending(self):
        return self.get_queryset().pending()
    
    def processing(self):
        return self.get_queryset().processing()


class Payment(models.Model):
    order_id = models.CharField(max_length=100, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True
    )
    gateway_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    gateway_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    timeout_count = models.PositiveIntegerField(default=0)
    last_timeout_at = models.DateTimeField(null=True, blank=True)
    
    objects = PaymentManager()
    
    class Meta:
        db_table = 'payments_payment'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Payment {self.id} - {self.order_id} ({self.status})"
    
    def mark_as_processing(self) -> None:
        self.status = PaymentStatus.PROCESSING
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_completed(self, transaction_id: str, response: str = '') -> None:
        self.status = PaymentStatus.COMPLETED
        self.gateway_transaction_id = transaction_id
        self.gateway_response = response
        self.save(update_fields=['status', 'gateway_transaction_id', 'gateway_response', 'updated_at'])
    
    def mark_as_failed(self, response: str = '') -> None:
        self.status = PaymentStatus.FAILED
        self.gateway_response = response
        self.save(update_fields=['status', 'gateway_response', 'updated_at'])
    
    def increment_timeout_count(self) -> None:
        self.timeout_count += 1
        self.last_timeout_at = timezone.now()
        self.save(update_fields=['timeout_count', 'last_timeout_at', 'updated_at'])
    
    @property
    def has_exceeded_timeout_limit(self) -> bool:
        return self.timeout_count >= 3
    
    @property
    def can_retry(self) -> bool:
        return self.status in [PaymentStatus.PENDING, PaymentStatus.TIMEOUT] and not self.has_exceeded_timeout_limit
```