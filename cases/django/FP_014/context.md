# Existing Codebase

## Schema

```sql
-- Users table with status field (low cardinality - only 3 possible values)
CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254),
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_staff BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User profiles with account status (intentionally no index on status)
CREATE TABLE accounts_userprofile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Orders table with existing indexes
CREATE TABLE orders_order (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    total DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX orders_order_user_id_idx ON orders_order(user_id);
CREATE INDEX orders_order_created_at_idx ON orders_order(created_at);
```

## Models

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from typing import Optional


class UserProfileStatus:
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    PENDING = 'pending'
    
    CHOICES = [
        (ACTIVE, 'Active'),
        (SUSPENDED, 'Suspended'),
        (PENDING, 'Pending Verification'),
    ]


class UserProfileQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=UserProfileStatus.ACTIVE)
    
    def suspended(self):
        return self.filter(status=UserProfileStatus.SUSPENDED)
    
    def pending_verification(self):
        return self.filter(status=UserProfileStatus.PENDING)


class UserProfileManager(models.Manager):
    def get_queryset(self):
        return UserProfileQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def suspended(self):
        return self.get_queryset().suspended()
    
    def pending_verification(self):
        return self.get_queryset().pending_verification()


class UserProfile(models.Model):
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='profile'
    )
    status = models.CharField(
        max_length=20,
        choices=UserProfileStatus.CHOICES,
        default=UserProfileStatus.ACTIVE
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserProfileManager()
    
    class Meta:
        db_table = 'accounts_userprofile'
    
    def is_active(self) -> bool:
        return self.status == UserProfileStatus.ACTIVE
    
    def suspend(self) -> None:
        self.status = UserProfileStatus.SUSPENDED
        self.save(update_fields=['status', 'updated_at'])
    
    def activate(self) -> None:
        self.status = UserProfileStatus.ACTIVE
        self.save(update_fields=['status', 'updated_at'])


class Order(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='orders'
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'orders_order'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]
```