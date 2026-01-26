# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE NULL
);

CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

## Models

```python
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from django.db.models import QuerySet


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class OrderQuerySet(models.QuerySet["Order"]):
    def pending(self) -> "QuerySet[Order]":
        return self.filter(status=OrderStatus.PENDING)
    
    def unprocessed(self) -> "QuerySet[Order]":
        return self.filter(processed_at__isnull=True)
    
    def by_status(self, status: OrderStatus) -> "QuerySet[Order]":
        return self.filter(status=status)
    
    def created_before(self, date) -> "QuerySet[Order]":
        return self.filter(created_at__lt=date)


class OrderManager(models.Manager["Order"]):
    def get_queryset(self) -> OrderQuerySet:
        return OrderQuerySet(self.model, using=self._db)
    
    def pending(self) -> "QuerySet[Order]":
        return self.get_queryset().pending()
    
    def unprocessed(self) -> "QuerySet[Order]":
        return self.get_queryset().unprocessed()


class Order(models.Model):
    customer_id = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    objects = OrderManager()
    
    class Meta:
        db_table = "orders"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["customer_id"]),
        ]
    
    def mark_as_processing(self) -> None:
        self.status = OrderStatus.PROCESSING
        self.save(update_fields=["status", "updated_at"])
    
    def mark_as_completed(self) -> None:
        self.status = OrderStatus.COMPLETED
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "processed_at", "updated_at"])
    
    def __str__(self) -> str:
        return f"Order {self.id} - {self.status}"


# Configuration constants
DEFAULT_BATCH_SIZE = 1000
MAX_BATCH_SIZE = 5000
PROCESSING_TIMEOUT_MINUTES = 30
```