# Existing Codebase

## Schema

```sql
CREATE TABLE notifications_notification (
    id BIGINT PRIMARY KEY,
    recipient_id BIGINT NOT NULL,
    sender_id BIGINT,
    notification_type VARCHAR(50) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    email_template VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP NULL,
    status VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE auth_user (
    id BIGINT PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE
);
```

## Models

```python
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from typing import Optional


class NotificationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    SENT = 'sent', 'Sent'
    FAILED = 'failed', 'Failed'


class NotificationQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status=NotificationStatus.PENDING)
    
    def for_recipient(self, user_id: int):
        return self.filter(recipient_id=user_id)
    
    def by_type(self, notification_type: str):
        return self.filter(notification_type=notification_type)


class NotificationManager(models.Manager):
    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)
    
    def pending(self):
        return self.get_queryset().pending()
    
    def create_notification(self, recipient: User, notification_type: str, 
                          subject: str, message: str, sender: Optional[User] = None,
                          email_template: Optional[str] = None):
        return self.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            subject=subject,
            message=message,
            email_template=email_template
        )


class Notification(models.Model):
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_notifications'
    )
    sender = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='sent_notifications'
    )
    notification_type = models.CharField(max_length=50)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    email_template = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING
    )
    
    objects = NotificationManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['notification_type', 'status']),
        ]
    
    def get_recipient_email(self) -> str:
        return self.recipient.email
    
    def get_recipient_name(self) -> str:
        if self.recipient.first_name and self.recipient.last_name:
            return f"{self.recipient.first_name} {self.recipient.last_name}"
        return self.recipient.username
    
    def mark_as_sent(self):
        self.status = NotificationStatus.SENT
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])
    
    def mark_as_failed(self):
        self.status = NotificationStatus.FAILED
        self.save(update_fields=['status'])
```