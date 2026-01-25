# Existing Codebase

## Schema

```sql
CREATE TABLE blog_post (
    id BIGINT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    author_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE NULL,
    FOREIGN KEY (author_id) REFERENCES auth_user (id)
);

CREATE INDEX blog_post_author_id_idx ON blog_post (author_id);
CREATE INDEX blog_post_status_idx ON blog_post (status);
CREATE INDEX blog_post_published_at_idx ON blog_post (published_at);
```

## Models

```python
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from typing import Optional


class PostStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'


class PublishedPostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            status=PostStatus.PUBLISHED,
            published_at__lte=timezone.now()
        )


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    status = models.CharField(
        max_length=20,
        choices=PostStatus.choices,
        default=PostStatus.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()
    published = PublishedPostManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', 'status']),
            models.Index(fields=['published_at']),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.title)
        
        if self.status == PostStatus.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        elif self.status != PostStatus.PUBLISHED:
            self.published_at = None
            
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    @property
    def is_published(self) -> bool:
        return (
            self.status == PostStatus.PUBLISHED and
            self.published_at and
            self.published_at <= timezone.now()
        )

    def can_edit(self, user: User) -> bool:
        return user.is_authenticated and (
            user == self.author or user.is_staff
        )

    def get_edit_url(self) -> str:
        return reverse('blog:post_edit', kwargs={'pk': self.pk})

    def get_delete_url(self) -> str:
        return reverse('blog:post_delete', kwargs={'pk': self.pk})
```