# Existing Codebase

## Schema

```sql
CREATE TABLE events_event (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    organizer_id INTEGER REFERENCES auth_user(id),
    timezone VARCHAR(50) DEFAULT 'UTC'
);

CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254),
    timezone VARCHAR(50) DEFAULT 'UTC'
);
```

## Models

```python
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime
import pytz


class User(AbstractUser):
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        choices=[(tz, tz) for tz in pytz.common_timezones]
    )
    
    def get_local_timezone(self) -> pytz.BaseTzInfo:
        return pytz.timezone(self.timezone)


class EventQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(start_time__gte=timezone.now())
    
    def for_date_range(self, start_date: datetime, end_date: datetime):
        return self.filter(
            start_time__gte=start_date,
            start_time__lt=end_date
        )


class EventManager(models.Manager):
    def get_queryset(self):
        return EventQuerySet(self.model, using=self._db)
    
    def upcoming(self):
        return self.get_queryset().upcoming()


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events'
    )
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        choices=[(tz, tz) for tz in pytz.common_timezones]
    )
    
    objects = EventManager()
    
    class Meta:
        ordering = ['start_time']
    
    def __str__(self) -> str:
        return self.title
    
    def get_event_timezone(self) -> pytz.BaseTzInfo:
        return pytz.timezone(self.timezone)
    
    def is_upcoming(self) -> bool:
        return self.start_time > timezone.now()
    
    def duration_minutes(self) -> int | None:
        if not self.end_time:
            return None
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)


# Common timezone choices for forms
COMMON_TIMEZONES = [
    ('UTC', 'UTC'),
    ('US/Eastern', 'Eastern Time'),
    ('US/Central', 'Central Time'),
    ('US/Mountain', 'Mountain Time'),
    ('US/Pacific', 'Pacific Time'),
    ('Europe/London', 'London'),
    ('Europe/Paris', 'Paris'),
    ('Asia/Tokyo', 'Tokyo'),
    ('Australia/Sydney', 'Sydney'),
]
```