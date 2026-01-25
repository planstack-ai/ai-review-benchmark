# Existing Codebase

## Schema

```sql
CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE points_point (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    amount INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_points_point_user_id ON points_point(user_id);
```

## Models

```python
from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


class PointQuerySet(QuerySet["Point"]):
    def for_user(self, user: "AbstractUser") -> QuerySet["Point"]:
        return self.filter(user=user)
    
    def active(self) -> QuerySet["Point"]:
        return self.filter(user__is_active=True)
    
    def recent(self) -> QuerySet["Point"]:
        return self.order_by('-created_at')


class PointManager(models.Manager["Point"]):
    def get_queryset(self) -> PointQuerySet:
        return PointQuerySet(self.model, using=self._db)
    
    def for_user(self, user: "AbstractUser") -> QuerySet["Point"]:
        return self.get_queryset().for_user(user)
    
    def active(self) -> QuerySet["Point"]:
        return self.get_queryset().active()


class Point(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='points'
    )
    amount = models.IntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = PointManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self) -> str:
        return f"{self.user.username}: {self.amount} points"
    
    @property
    def is_positive(self) -> bool:
        return self.amount > 0
    
    def belongs_to_user(self, user: "AbstractUser") -> bool:
        return self.user_id == user.id


# Existing view mixins and utilities
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404


class UserOwnedObjectMixin:
    """Base mixin for views that should only show user's own objects."""
    
    def get_object(self):
        obj = super().get_object()
        if hasattr(obj, 'user') and obj.user != self.request.user:
            raise Http404("Object not found")
        return obj


class PointsBaseView(LoginRequiredMixin):
    model = Point
    context_object_name = 'points'
    
    def get_base_queryset(self):
        return Point.objects.active().recent()
```