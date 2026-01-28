# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    payment_intent_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL
);
```

## Models

```python
from decimal import Decimal
from typing import Optional
from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    PAID = 'paid', 'Paid'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'


class OrderQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status=OrderStatus.PENDING)
    
    def paid(self):
        return self.filter(status=OrderStatus.PAID)
    
    def for_user(self, user: User):
        return self.filter(user=user)


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)
    
    def pending(self):
        return self.get_queryset().pending()
    
    def paid(self):
        return self.get_queryset().paid()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderManager()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Order #{self.id} - {self.user.username}"
    
    def calculate_total(self) -> Decimal:
        return sum(item.subtotal for item in self.items.all())
    
    def mark_as_processing(self) -> None:
        self.status = OrderStatus.PROCESSING
        self.updated_at = timezone.now()
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_paid(self, payment_intent_id: str) -> None:
        self.status = OrderStatus.PAID
        self.payment_intent_id = payment_intent_id
        self.updated_at = timezone.now()
        self.save(update_fields=['status', 'payment_intent_id', 'updated_at'])
    
    def mark_as_failed(self) -> None:
        self.status = OrderStatus.FAILED
        self.updated_at = timezone.now()
        self.save(update_fields=['status', 'updated_at'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_id = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ['order', 'product_id']
    
    @property
    def subtotal(self) -> Decimal:
        return self.price * self.quantity


class PaymentService:
    @staticmethod
    def create_payment_intent(amount: Decimal, currency: str = 'usd') -> dict:
        """Creates a payment intent with external payment provider."""
        pass
    
    @staticmethod
    def confirm_payment(payment_intent_id: str) -> dict:
        """Confirms payment with external payment provider."""
        pass
    
    @staticmethod
    def cancel_payment(payment_intent_id: str) -> dict:
        """Cancels payment with external payment provider."""
        pass


class NotificationService:
    @staticmethod
    def send_order_confirmation(order: Order) -> bool:
        """Sends order confirmation email to customer."""
        pass
    
    @staticmethod
    def send_payment_failed_notification(order: Order) -> bool:
        """Sends payment failure notification to customer."""
        pass
```