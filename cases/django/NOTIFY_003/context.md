# Existing Codebase

## Schema

```sql
-- payments_payment table
CREATE TABLE payments_payment (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    payment_method VARCHAR(50),
    transaction_id VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id)
);

-- notifications_notification table
CREATE TABLE notifications_notification (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user(id)
);
```

## Models

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from typing import Optional
import uuid


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'


class PaymentQuerySet(models.QuerySet):
    def confirmed(self):
        return self.filter(status=PaymentStatus.CONFIRMED)
    
    def pending(self):
        return self.filter(status=PaymentStatus.PENDING)
    
    def for_user(self, user: User):
        return self.filter(user=user)


class PaymentManager(models.Manager):
    def get_queryset(self):
        return PaymentQuerySet(self.model, using=self._db)
    
    def confirmed(self):
        return self.get_queryset().confirmed()
    
    def pending(self):
        return self.get_queryset().pending()


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    objects = PaymentManager()
    
    class Meta:
        db_table = 'payments_payment'
        ordering = ['-created_at']
    
    def confirm_payment(self) -> bool:
        if self.status == PaymentStatus.PENDING:
            self.status = PaymentStatus.CONFIRMED
            self.confirmed_at = timezone.now()
            self.save(update_fields=['status', 'confirmed_at'])
            return True
        return False


class NotificationType(models.TextChoices):
    PAYMENT_CONFIRMED = 'payment_confirmed', 'Payment Confirmed'
    PAYMENT_FAILED = 'payment_failed', 'Payment Failed'
    ACCOUNT_UPDATE = 'account_update', 'Account Update'


class NotificationManager(models.Manager):
    def create_payment_confirmation(self, user: User, payment: Payment):
        return self.create(
            user=user,
            type=NotificationType.PAYMENT_CONFIRMED,
            title=f'Payment Confirmed - ${payment.amount}',
            message=f'Your payment of ${payment.amount} has been successfully processed.',
            data={'payment_id': payment.id, 'amount': str(payment.amount)}
        )
    
    def unread_for_user(self, user: User):
        return self.filter(user=user, is_read=False)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=50, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = NotificationManager()
    
    class Meta:
        db_table = 'notifications_notification'
        ordering = ['-created_at']
```