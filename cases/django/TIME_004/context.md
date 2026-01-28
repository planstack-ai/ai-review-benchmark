# Existing Codebase

## Schema

```sql
CREATE TABLE events_event (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE events_eventregistration (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events_event(id),
    user_email VARCHAR(254) NOT NULL,
    registered_at TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
);
```

## Models

```python
from datetime import datetime, date
from typing import Optional
from django.db import models
from django.utils import timezone


class EventQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)
    
    def upcoming(self):
        return self.filter(event_date__gt=timezone.now())
    
    def past(self):
        return self.filter(event_date__lt=timezone.now())


class EventManager(models.Manager):
    def get_queryset(self):
        return EventQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def upcoming(self):
        return self.get_queryset().upcoming()


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    objects = EventManager()
    
    class Meta:
        ordering = ['event_date']
    
    def __str__(self) -> str:
        return self.title
    
    @property
    def is_today(self) -> bool:
        today = timezone.now().date()
        return self.event_date.date() == today
    
    @property
    def is_past(self) -> bool:
        return self.event_date < timezone.now()
    
    def get_date_display(self) -> str:
        return self.event_date.strftime('%Y-%m-%d')


class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user_email = models.EmailField()
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        unique_together = ['event', 'user_email']
    
    def __str__(self) -> str:
        return f"{self.user_email} - {self.event.title}"


class EventService:
    @staticmethod
    def get_events_by_date_range(start_date: date, end_date: date):
        return Event.objects.active().filter(
            event_date__date__gte=start_date,
            event_date__date__lte=end_date
        )
    
    @staticmethod
    def count_registrations_by_date(target_date: date) -> int:
        return EventRegistration.objects.filter(
            registered_at__date=target_date,
            status='confirmed'
        ).count()
```