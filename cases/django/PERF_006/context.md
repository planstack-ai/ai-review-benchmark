# Existing Codebase

## Schema

```sql
CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE profiles_userprofile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES auth_user(id),
    bio TEXT,
    avatar VARCHAR(100),
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE posts_post (
    id SERIAL PRIMARY KEY,
    author_id INTEGER REFERENCES auth_user(id),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

## Models

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.cache import cache
from django.utils import timezone
from typing import Optional, Dict, Any
import hashlib


class User(AbstractUser):
    """Extended user model with additional fields."""
    
    def get_cache_prefix(self) -> str:
        """Generate a unique cache prefix for this user."""
        return f"user_{self.pk}"
    
    def invalidate_user_cache(self) -> None:
        """Clear all cache entries for this user."""
        prefix = self.get_cache_prefix()
        # Implementation would clear cache entries with this prefix
        pass


class UserProfile(models.Model):
    """User profile with preferences and metadata."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    preferences = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profiles_userprofile'


class PostQuerySet(models.QuerySet):
    """Custom queryset for Post model."""
    
    def published(self):
        return self.filter(status='published')
    
    def for_user(self, user: User):
        return self.filter(author=user)
    
    def recent(self, days: int = 30):
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(created_at__gte=cutoff)


class PostManager(models.Manager):
    """Custom manager for Post model."""
    
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)
    
    def published(self):
        return self.get_queryset().published()
    
    def for_user(self, user: User):
        return self.get_queryset().for_user(user)


class Post(models.Model):
    """Blog post model."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = PostManager()
    
    class Meta:
        db_table = 'posts_post'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self) -> str:
        return f"/posts/{self.pk}/"


# Cache configuration constants
CACHE_TIMEOUT_SHORT = 300  # 5 minutes
CACHE_TIMEOUT_MEDIUM = 1800  # 30 minutes
CACHE_TIMEOUT_LONG = 3600  # 1 hour

# Cache key patterns
CACHE_KEY_PATTERNS = {
    'user_posts': 'posts:user:{user_id}:page:{page}',
    'user_profile': 'profile:user:{user_id}',
    'user_stats': 'stats:user:{user_id}',
    'post_detail': 'post:{post_id}:user:{user_id}',
}
```