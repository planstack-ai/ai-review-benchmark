# Existing Codebase

## Schema

```sql
CREATE TABLE analytics_event (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    event_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    properties JSONB,
    session_id UUID,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_analytics_event_user_timestamp ON analytics_event(user_id, timestamp DESC);
CREATE INDEX idx_analytics_event_type_timestamp ON analytics_event(event_type, timestamp DESC);
CREATE INDEX idx_analytics_event_session ON analytics_event(session_id);
CREATE INDEX idx_analytics_event_timestamp ON analytics_event(timestamp DESC);
```

## Models

```python
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from typing import Dict, Any, Optional
import uuid


class EventType(models.TextChoices):
    PAGE_VIEW = 'page_view', 'Page View'
    CLICK = 'click', 'Click'
    FORM_SUBMIT = 'form_submit', 'Form Submit'
    PURCHASE = 'purchase', 'Purchase'
    LOGIN = 'login', 'Login'
    LOGOUT = 'logout', 'Logout'


class AnalyticsEventManager(models.Manager):
    def for_user(self, user_id: int):
        return self.filter(user_id=user_id)
    
    def by_type(self, event_type: str):
        return self.filter(event_type=event_type)
    
    def in_date_range(self, start_date, end_date):
        return self.filter(timestamp__range=(start_date, end_date))
    
    def recent(self, days: int = 30):
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(timestamp__gte=cutoff)


class AnalyticsEvent(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='analytics_events'
    )
    event_type = models.CharField(max_length=50, choices=EventType.choices)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    properties = models.JSONField(default=dict, blank=True)
    session_id = models.UUIDField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = AnalyticsEventManager()
    
    class Meta:
        db_table = 'analytics_event'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['event_type', '-timestamp']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self) -> str:
        return f"{self.event_type} - {self.timestamp}"
    
    @property
    def is_authenticated_event(self) -> bool:
        return self.user_id is not None


class UserSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    started_at = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_session'
        ordering = ['-started_at']
    
    def update_activity(self):
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    @property
    def duration(self) -> timezone.timedelta:
        return self.last_activity - self.started_at
```