# Existing Codebase

## Schema

```sql
CREATE TABLE webhook_events (
    id BIGSERIAL PRIMARY KEY,
    external_id VARCHAR(255) UNIQUE NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    processed_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_webhook_events_external_id ON webhook_events(external_id);
CREATE INDEX idx_webhook_events_processed_at ON webhook_events(processed_at);
CREATE INDEX idx_webhook_events_event_type ON webhook_events(event_type);
```

## Models

```python
from django.db import models, transaction
from django.utils import timezone
from typing import Optional, Dict, Any
import json


class WebhookEventQuerySet(models.QuerySet):
    def unprocessed(self) -> 'WebhookEventQuerySet':
        return self.filter(processed_at__isnull=True)
    
    def processed(self) -> 'WebhookEventQuerySet':
        return self.filter(processed_at__isnull=False)
    
    def by_event_type(self, event_type: str) -> 'WebhookEventQuerySet':
        return self.filter(event_type=event_type)


class WebhookEventManager(models.Manager):
    def get_queryset(self) -> WebhookEventQuerySet:
        return WebhookEventQuerySet(self.model, using=self._db)
    
    def unprocessed(self) -> WebhookEventQuerySet:
        return self.get_queryset().unprocessed()
    
    def processed(self) -> WebhookEventQuerySet:
        return self.get_queryset().processed()


class WebhookEvent(models.Model):
    external_id = models.CharField(max_length=255, unique=True, db_index=True)
    event_type = models.CharField(max_length=100, db_index=True)
    payload = models.JSONField()
    processed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = WebhookEventManager()
    
    class Meta:
        db_table = 'webhook_events'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"WebhookEvent({self.external_id}, {self.event_type})"
    
    @property
    def is_processed(self) -> bool:
        return self.processed_at is not None
    
    def mark_as_processed(self) -> None:
        self.processed_at = timezone.now()
        self.save(update_fields=['processed_at', 'updated_at'])
    
    def get_payload_data(self) -> Dict[str, Any]:
        if isinstance(self.payload, str):
            return json.loads(self.payload)
        return self.payload


class WebhookProcessor:
    """Base processor for handling webhook events."""
    
    def __init__(self):
        self.handlers = {
            'user.created': self._handle_user_created,
            'user.updated': self._handle_user_updated,
            'payment.completed': self._handle_payment_completed,
        }
    
    def process_event(self, event: WebhookEvent) -> bool:
        handler = self.handlers.get(event.event_type)
        if not handler:
            return False
        
        try:
            handler(event.get_payload_data())
            return True
        except Exception:
            return False
    
    def _handle_user_created(self, payload: Dict[str, Any]) -> None:
        # Implementation would go here
        pass
    
    def _handle_user_updated(self, payload: Dict[str, Any]) -> None:
        # Implementation would go here
        pass
    
    def _handle_payment_completed(self, payload: Dict[str, Any]) -> None:
        # Implementation would go here
        pass
```