# Existing Codebase

## Schema

```sql
-- Core tables for analytics system
CREATE TABLE analytics_event (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    session_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET
);

CREATE TABLE analytics_session (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES auth_user(id),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    user_agent TEXT,
    referrer TEXT
);

CREATE INDEX idx_analytics_event_user_created ON analytics_event(user_id, created_at);
CREATE INDEX idx_analytics_event_session_type ON analytics_event(session_id, event_type);
CREATE INDEX idx_analytics_session_user_started ON analytics_session(user_id, started_at);
```

## Models

```python
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from typing import Dict, Any, Optional
import uuid


class AnalyticsSessionManager(models.Manager):
    def active_sessions(self):
        return self.filter(ended_at__isnull=True)
    
    def for_user(self, user_id: int):
        return self.filter(user_id=user_id)


class AnalyticsSession(models.Model):
    session_id = models.CharField(max_length=64, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.TextField(blank=True)
    
    objects = AnalyticsSessionManager()
    
    class Meta:
        db_table = 'analytics_session'
        indexes = [
            models.Index(fields=['user', 'started_at']),
        ]
    
    def __str__(self) -> str:
        return f"Session {self.session_id[:8]}..."
    
    @property
    def duration(self) -> Optional[timezone.timedelta]:
        if self.ended_at:
            return self.ended_at - self.started_at
        return None


class AnalyticsEventManager(models.Manager):
    def for_session(self, session_id: str):
        return self.filter(session_id=session_id)
    
    def by_type(self, event_type: str):
        return self.filter(event_type=event_type)
    
    def in_date_range(self, start_date, end_date):
        return self.filter(created_at__range=(start_date, end_date))


class AnalyticsEvent(models.Model):
    EVENT_TYPES = [
        ('page_view', 'Page View'),
        ('click', 'Click'),
        ('form_submit', 'Form Submit'),
        ('purchase', 'Purchase'),
        ('signup', 'User Signup'),
        ('login', 'User Login'),
        ('logout', 'User Logout'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=64, db_index=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    objects = AnalyticsEventManager()
    
    class Meta:
        db_table = 'analytics_event'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['session_id', 'event_type']),
        ]
    
    def __str__(self) -> str:
        return f"{self.event_type} at {self.created_at}"


class UserAnalyticsProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='analytics_profile')
    total_sessions = models.PositiveIntegerField(default=0)
    total_events = models.PositiveIntegerField(default=0)
    first_seen = models.DateTimeField(null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    
    def update_stats(self):
        from django.db.models import Count, Min, Max
        stats = AnalyticsEvent.objects.filter(user=self.user).aggregate(
            total_events=Count('id'),
            first_seen=Min('created_at'),
            last_seen=Max('created_at')
        )
        session_count = AnalyticsSession.objects.filter(user=self.user).count()
        
        self.total_events = stats['total_events'] or 0
        self.total_sessions = session_count
        self.first_seen = stats['first_seen']
        self.last_seen = stats['last_seen']
        self.save()
```