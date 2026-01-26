# Existing Codebase

## Schema

```sql
CREATE TABLE notifications_notification (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE NULL,
    error_message TEXT NULL,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3
);

CREATE INDEX idx_notifications_status ON notifications_notification(status);
CREATE INDEX idx_notifications_user_created ON notifications_notification(user_id, created_at);
```

## Models

```python
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from typing import Optional
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    SENT = 'sent', 'Sent'
    FAILED = 'failed', 'Failed'
    RETRYING = 'retrying', 'Retrying'


class NotificationType(models.TextChoices):
    EMAIL = 'email', 'Email'
    SMS = 'sms', 'SMS'
    PUSH = 'push', 'Push Notification'
    WEBHOOK = 'webhook', 'Webhook'


class NotificationQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status=NotificationStatus.PENDING)
    
    def failed(self):
        return self.filter(status=NotificationStatus.FAILED)
    
    def can_retry(self):
        return self.filter(
            status__in=[NotificationStatus.FAILED, NotificationStatus.RETRYING],
            retry_count__lt=models.F('max_retries')
        )


class NotificationManager(models.Manager):
    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)
    
    def pending(self):
        return self.get_queryset().pending()
    
    def failed(self):
        return self.get_queryset().failed()
    
    def can_retry(self):
        return self.get_queryset().can_retry()


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.EMAIL
    )
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    
    objects = NotificationManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def mark_as_sent(self) -> None:
        self.status = NotificationStatus.SENT
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])
    
    def mark_as_failed(self, error_message: str) -> None:
        self.status = NotificationStatus.FAILED
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message'])
    
    def increment_retry_count(self) -> None:
        self.retry_count += 1
        self.status = NotificationStatus.RETRYING if self.can_retry else NotificationStatus.FAILED
        self.save(update_fields=['retry_count', 'status'])
    
    @property
    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries
    
    def __str__(self) -> str:
        return f"{self.title} ({self.get_notification_type_display()}) - {self.user.email}"
```