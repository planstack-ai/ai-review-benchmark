# Existing Codebase

## Schema

```sql
CREATE TABLE events_event (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_events_start_date ON events_event(start_date);
CREATE INDEX idx_events_end_date ON events_event(end_date);
CREATE INDEX idx_events_date_range ON events_event(start_date, end_date);
```

## Models

```python
from datetime import date, datetime, timedelta
from typing import Optional

from django.db import models
from django.db.models import Q, QuerySet
from django.utils import timezone


class EventQuerySet(models.QuerySet):
    def active(self) -> QuerySet:
        """Return events that are currently active."""
        today = timezone.now().date()
        return self.filter(start_date__lte=today, end_date__gte=today)
    
    def in_date_range(self, start: date, end: date) -> QuerySet:
        """Return events that overlap with the given date range."""
        return self.filter(
            Q(start_date__lte=end) & Q(end_date__gte=start)
        )
    
    def starting_in_period(self, start: date, end: date) -> QuerySet:
        """Return events that start within the given period."""
        return self.filter(start_date__gte=start, start_date__lte=end)


class EventManager(models.Manager):
    def get_queryset(self) -> EventQuerySet:
        return EventQuerySet(self.model, using=self._db)
    
    def active(self) -> QuerySet:
        return self.get_queryset().active()
    
    def in_date_range(self, start: date, end: date) -> QuerySet:
        return self.get_queryset().in_date_range(start, end)


class Event(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = EventManager()
    
    class Meta:
        db_table = 'events_event'
        ordering = ['start_date', 'name']
    
    def __str__(self) -> str:
        return self.name
    
    @property
    def duration_days(self) -> int:
        """Calculate the duration of the event in days."""
        return (self.end_date - self.start_date).days + 1
    
    def is_active(self, reference_date: Optional[date] = None) -> bool:
        """Check if the event is active on the given date."""
        if reference_date is None:
            reference_date = timezone.now().date()
        return self.start_date <= reference_date <= self.end_date
    
    def overlaps_with(self, other_start: date, other_end: date) -> bool:
        """Check if this event overlaps with another date range."""
        return self.start_date <= other_end and self.end_date >= other_start


class DateRange:
    """Utility class for working with date ranges."""
    
    def __init__(self, start: date, end: date):
        if start > end:
            raise ValueError("Start date must be before or equal to end date")
        self.start = start
        self.end = end
    
    @classmethod
    def from_year(cls, year: int) -> 'DateRange':
        """Create a date range for an entire year."""
        return cls(date(year, 1, 1), date(year, 12, 31))
    
    @classmethod
    def last_n_days(cls, days: int, reference_date: Optional[date] = None) -> 'DateRange':
        """Create a date range for the last N days."""
        if reference_date is None:
            reference_date = timezone.now().date()
        start = reference_date - timedelta(days=days - 1)
        return cls(start, reference_date)
    
    def contains(self, check_date: date) -> bool:
        """Check if the given date falls within this range."""
        return self.start <= check_date <= self.end
    
    def overlaps(self, other: 'DateRange') -> bool:
        """Check if this range overlaps with another range."""
        return self.start <= other.end and self.end >= other.start
```