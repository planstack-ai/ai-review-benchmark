# Existing Codebase

## Schema

```sql
CREATE TABLE notifications_emailprovider (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    max_emails_per_minute INTEGER NOT NULL DEFAULT 60,
    max_emails_per_hour INTEGER NOT NULL DEFAULT 1000,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE notifications_notification (
    id SERIAL PRIMARY KEY,
    recipient_email VARCHAR(254) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    body TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    provider_id INTEGER REFERENCES notifications_emailprovider(id),
    scheduled_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_notification_status_scheduled ON notifications_notification(status, scheduled_at);
CREATE INDEX idx_notification_provider_sent ON notifications_notification(provider_id, sent_at);
```

## Models

```python
from django.db import models
from django.utils import timezone
from datetime import timedelta
from typing import Optional


class NotificationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    SENT = 'sent', 'Sent'
    FAILED = 'failed', 'Failed'
    RATE_LIMITED = 'rate_limited', 'Rate Limited'


class EmailProviderManager(models.Manager):
    def get_active_providers(self):
        return self.filter(is_active=True)
    
    def get_least_loaded_provider(self):
        """Returns provider with lowest recent usage"""
        now = timezone.now()
        hour_ago = now - timedelta(hours=1)
        
        return self.get_active_providers().annotate(
            recent_count=models.Count(
                'notifications',
                filter=models.Q(
                    notifications__sent_at__gte=hour_ago,
                    notifications__status=NotificationStatus.SENT
                )
            )
        ).order_by('recent_count').first()


class EmailProvider(models.Model):
    name = models.CharField(max_length=100)
    max_emails_per_minute = models.PositiveIntegerField(default=60)
    max_emails_per_hour = models.PositiveIntegerField(default=1000)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = EmailProviderManager()
    
    def get_sent_count_in_period(self, minutes: int) -> int:
        """Count emails sent by this provider in the last N minutes"""
        cutoff = timezone.now() - timedelta(minutes=minutes)
        return self.notifications.filter(
            sent_at__gte=cutoff,
            status=NotificationStatus.SENT
        ).count()
    
    def can_send_email(self) -> bool:
        """Check if provider can send email without exceeding rate limits"""
        minute_count = self.get_sent_count_in_period(1)
        hour_count = self.get_sent_count_in_period(60)
        
        return (minute_count < self.max_emails_per_minute and 
                hour_count < self.max_emails_per_hour)
    
    def __str__(self):
        return self.name


class NotificationQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status=NotificationStatus.PENDING)
    
    def ready_to_send(self):
        now = timezone.now()
        return self.pending().filter(
            models.Q(scheduled_at__isnull=True) | 
            models.Q(scheduled_at__lte=now)
        )
    
    def rate_limited(self):
        return self.filter(status=NotificationStatus.RATE_LIMITED)


class NotificationManager(models.Manager):
    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)
    
    def pending(self):
        return self.get_queryset().pending()
    
    def ready_to_send(self):
        return self.get_queryset().ready_to_send()


class Notification(models.Model):
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING
    )
    provider = models.ForeignKey(
        EmailProvider,
        on_delete=models.SET_NULL,
        null=True,
        related_name='notifications'
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = NotificationManager()
    
    def mark_as_sent(self, provider: Optional[EmailProvider] = None):
        self.status = NotificationStatus.SENT
        self.sent_at = timezone.now()
        if provider:
            self.provider = provider
        self.save(update_fields=['status', 'sent_at', 'provider', 'updated_at'])
    
    def mark_as_rate_limited(self):
        self.status = NotificationStatus.RATE_LIMITED
        self.save(update_fields=['status', 'updated_at'])
```