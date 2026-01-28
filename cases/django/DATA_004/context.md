# Existing Codebase

## Schema

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    deleted_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    author_id INTEGER REFERENCES users(id),
    is_published BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    post_id INTEGER REFERENCES posts(id),
    author_id INTEGER REFERENCES users(id),
    deleted_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Models

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from typing import Optional


class BaseModel(models.Model):
    """Base model with common fields and soft delete functionality."""
    
    deleted_at: Optional[timezone.datetime] = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False) -> tuple[int, dict[str, int]]:
        """Soft delete by setting deleted_at timestamp."""
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=['deleted_at'])
        return 1, {self._meta.label: 1}
    
    def hard_delete(self, using=None, keep_parents=False) -> tuple[int, dict[str, int]]:
        """Permanently delete the record."""
        return super().delete(using=using, keep_parents=keep_parents)
    
    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])
    
    @property
    def is_deleted(self) -> bool:
        """Check if the record is soft-deleted."""
        return self.deleted_at is not None


class User(AbstractUser, BaseModel):
    """Custom user model with soft delete capability."""
    
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Post(BaseModel):
    """Blog post model."""
    
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    is_published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return self.title


class Comment(BaseModel):
    """Comment model for posts."""
    
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self) -> str:
        return f'Comment by {self.author.username} on {self.post.title}'
```