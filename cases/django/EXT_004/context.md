# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    external_reference VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, external_reference)
);

CREATE INDEX idx_orders_user_status ON orders(user_id, status);
CREATE INDEX idx_orders_external_ref ON orders(external_reference);
```

## Models

```python
from decimal import Decimal
from typing import Optional
from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'


class OrderManager(models.Manager):
    def get_by_reference(self, user: User, external_reference: str) -> Optional['Order']:
        try:
            return self.get(user=user, external_reference=external_reference)
        except self.model.DoesNotExist:
            return None
    
    def pending_orders(self):
        return self.filter(status=OrderStatus.PENDING)
    
    def failed_orders(self):
        return self.filter(status=OrderStatus.FAILED)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    external_reference = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=50,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderManager()
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'external_reference'],
                name='unique_user_external_reference',
                condition=models.Q(external_reference__isnull=False) & ~models.Q(external_reference='')
            )
        ]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['external_reference']),
        ]
    
    def __str__(self) -> str:
        return f"Order {self.id} - {self.user.username} - {self.status}"
    
    def can_retry(self) -> bool:
        return self.status in [OrderStatus.FAILED, OrderStatus.CANCELLED]
    
    def mark_processing(self) -> None:
        self.status = OrderStatus.PROCESSING
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_completed(self) -> None:
        self.status = OrderStatus.COMPLETED
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_failed(self) -> None:
        self.status = OrderStatus.FAILED
        self.save(update_fields=['status', 'updated_at'])


class OrderService:
    @staticmethod
    def process_order(order: Order) -> bool:
        """Simulate order processing logic"""
        try:
            order.mark_processing()
            # External payment processing would happen here
            order.mark_completed()
            return True
        except Exception:
            order.mark_failed()
            return False
```