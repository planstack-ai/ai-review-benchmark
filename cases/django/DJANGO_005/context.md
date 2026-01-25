# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    is_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

## Models

```python
from decimal import Decimal
from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from typing import Optional


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'


class OrderQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status=OrderStatus.PENDING)
    
    def confirmed(self):
        return self.filter(status=OrderStatus.CONFIRMED)
    
    def for_user(self, user_id: int):
        return self.filter(user_id=user_id)


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)
    
    def pending(self):
        return self.get_queryset().pending()
    
    def confirmed(self):
        return self.get_queryset().confirmed()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderManager()
    
    class Meta:
        ordering = ['-created_at']
    
    def calculate_total(self) -> Decimal:
        return sum(item.subtotal for item in self.items.all())
    
    def can_be_cancelled(self) -> bool:
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.price


class NotificationType(models.TextChoices):
    ORDER_CONFIRMATION = 'order_confirmation', 'Order Confirmation'
    ORDER_SHIPPED = 'order_shipped', 'Order Shipped'
    ORDER_DELIVERED = 'order_delivered', 'Order Delivered'
    PAYMENT_RECEIVED = 'payment_received', 'Payment Received'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices
    )
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


# Background task functions
def send_order_confirmation_email(order_id: int) -> None:
    """Send order confirmation email to customer."""
    pass


def update_inventory(order_id: int) -> None:
    """Update product inventory after order confirmation."""
    pass


def process_payment_webhook(order_id: int, payment_data: dict) -> None:
    """Process payment webhook data."""
    pass


def send_notification_email(notification_id: int) -> None:
    """Send notification email to user."""
    pass
```