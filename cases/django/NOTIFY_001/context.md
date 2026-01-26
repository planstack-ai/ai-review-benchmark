# Existing Codebase

## Schema

```sql
CREATE TABLE orders_order (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    email VARCHAR(254) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    total DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    confirmation_sent_at TIMESTAMP WITH TIME ZONE NULL
);

CREATE TABLE orders_orderitem (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders_order(id),
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE INDEX idx_orders_order_user_id ON orders_order(user_id);
CREATE INDEX idx_orders_order_status ON orders_order(status);
CREATE INDEX idx_orders_order_confirmation_sent ON orders_order(confirmation_sent_at);
```

## Models

```python
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from typing import Optional

User = get_user_model()


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'


class OrderQuerySet(models.QuerySet):
    def confirmed(self):
        return self.filter(status=OrderStatus.CONFIRMED)
    
    def pending_confirmation(self):
        return self.filter(
            status=OrderStatus.CONFIRMED,
            confirmation_sent_at__isnull=True
        )


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)
    
    def confirmed(self):
        return self.get_queryset().confirmed()
    
    def pending_confirmation(self):
        return self.get_queryset().pending_confirmation()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    email = models.EmailField()
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmation_sent_at = models.DateTimeField(null=True, blank=True)
    
    objects = OrderManager()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Order #{self.id} - {self.user.email}"
    
    @property
    def is_confirmation_sent(self) -> bool:
        return self.confirmation_sent_at is not None
    
    def mark_confirmation_sent(self) -> None:
        self.confirmation_sent_at = timezone.now()
        self.save(update_fields=['confirmation_sent_at'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self) -> str:
        return f"{self.quantity}x {self.product_name}"
    
    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.price


class EmailService:
    @staticmethod
    def send_order_confirmation(order: Order) -> bool:
        subject = f"Order Confirmation #{order.id}"
        message = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'items': order.items.all()
        })
        
        try:
            send_mail(
                subject=subject,
                message='',
                html_message=message,
                from_email='orders@example.com',
                recipient_list=[order.email],
                fail_silently=False
            )
            return True
        except Exception:
            return False
```