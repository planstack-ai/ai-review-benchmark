# Existing Codebase

## Schema

```sql
CREATE TABLE blog_post (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL REFERENCES auth_user(id),
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX blog_post_author_id_idx ON blog_post(author_id);
CREATE INDEX blog_post_status_idx ON blog_post(status);
```

## Models

```python
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from typing import Optional


class PostStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=PostStatus.PUBLISHED)
    
    def by_author(self, author: User):
        return self.filter(author=author)
    
    def recent(self, days: int = 30):
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(created_at__gte=cutoff)


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)
    
    def published(self):
        return self.get_queryset().published()
    
    def create_post(self, title: str, content: str, author: User) -> 'Post':
        return self.create(
            title=title,
            content=content,
            author=author,
            status=PostStatus.DRAFT
        )


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    status = models.CharField(
        max_length=20,
        choices=PostStatus.choices,
        default=PostStatus.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.PositiveIntegerField(default=1)
    
    objects = PostManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self) -> str:
        return self.title
    
    def can_edit(self, user: User) -> bool:
        return self.author == user or user.is_staff
    
    def publish(self) -> None:
        if self.status != PostStatus.DRAFT:
            raise ValidationError("Only draft posts can be published")
        self.status = PostStatus.PUBLISHED
        self.save(update_fields=['status', 'updated_at'])
    
    def archive(self) -> None:
        if self.status == PostStatus.ARCHIVED:
            raise ValidationError("Post is already archived")
        self.status = PostStatus.ARCHIVED
        self.save(update_fields=['status', 'updated_at'])


class PostRevision(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='revisions')
    title = models.CharField(max_length=200)
    content = models.TextField()
    version = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-version']
        unique_together = ['post', 'version']
```