# Existing Codebase

## Schema

```sql
CREATE TABLE analytics_event (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    user_id BIGINT,
    session_id VARCHAR(100),
    data JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_analytics_event_timestamp ON analytics_event(timestamp);
CREATE INDEX idx_analytics_event_processed ON analytics_event(processed);
CREATE INDEX idx_analytics_event_type ON analytics_event(event_type);
```

## Models

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from typing import Dict, Any, List, Optional
import asyncio
from asgiref.sync import sync_to_async


class EventType(models.TextChoices):
    PAGE_VIEW = 'page_view', 'Page View'
    CLICK = 'click', 'Click'
    FORM_SUBMIT = 'form_submit', 'Form Submit'
    API_CALL = 'api_call', 'API Call'
    ERROR = 'error', 'Error'


class AnalyticsEventQuerySet(models.QuerySet):
    def unprocessed(self):
        return self.filter(processed=False)
    
    def by_type(self, event_type: str):
        return self.filter(event_type=event_type)
    
    def recent(self, hours: int = 24):
        cutoff = timezone.now() - timezone.timedelta(hours=hours)
        return self.filter(timestamp__gte=cutoff)


class AnalyticsEventManager(models.Manager):
    def get_queryset(self):
        return AnalyticsEventQuerySet(self.model, using=self._db)
    
    def unprocessed(self):
        return self.get_queryset().unprocessed()
    
    def by_type(self, event_type: str):
        return self.get_queryset().by_type(event_type)


class AnalyticsEvent(models.Model):
    event_type = models.CharField(
        max_length=50,
        choices=EventType.choices,
        db_index=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    session_id = models.CharField(max_length=100, null=True, blank=True)
    data = models.JSONField(default=dict)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    processed = models.BooleanField(default=False, db_index=True)
    
    objects = AnalyticsEventManager()
    
    class Meta:
        db_table = 'analytics_event'
        ordering = ['-timestamp']
    
    def __str__(self) -> str:
        return f"{self.event_type} - {self.timestamp}"
    
    def mark_processed(self) -> None:
        self.processed = True
        self.save(update_fields=['processed'])


class EventBatch:
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self.events: List[Dict[str, Any]] = []
    
    def add_event(self, event_data: Dict[str, Any]) -> None:
        self.events.append(event_data)
    
    def is_full(self) -> bool:
        return len(self.events) >= self.batch_size
    
    def clear(self) -> None:
        self.events.clear()
    
    def size(self) -> int:
        return len(self.events)


class EventProcessor:
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self._processing_lock = asyncio.Lock()
    
    async def process_events(self, events: List[AnalyticsEvent]) -> int:
        processed_count = 0
        for event in events:
            await self._process_single_event(event)
            processed_count += 1
        return processed_count
    
    async def _process_single_event(self, event: AnalyticsEvent) -> None:
        # Simulate processing time
        await asyncio.sleep(0.001)
        await sync_to_async(event.mark_processed)()


# Configuration constants
BATCH_SIZE = 1000
MAX_CONCURRENT_WRITES = 10
WRITE_TIMEOUT_SECONDS = 30
```