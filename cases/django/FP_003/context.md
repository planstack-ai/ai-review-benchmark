# Existing Codebase

## Schema

```sql
CREATE TABLE blog_post (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL REFERENCES auth_user(id),
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE NULL,
    view_count INTEGER NOT NULL DEFAULT 0,
    is_featured BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE blog_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE blog_post_categories (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES blog_post(id),
    category_id INTEGER NOT NULL REFERENCES blog_category(id),
    UNIQUE(post_id, category_id)
);

CREATE INDEX idx_blog_post_status ON blog_post(status);
CREATE INDEX idx_blog_post_published_at ON blog_post(published_at);
CREATE INDEX idx_blog_post_author ON blog_post(author_id);
```

## Models

```python
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
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


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    categories = models.ManyToManyField(Category, related_name='posts', blank=True)
    status = models.CharField(
        max_length=20,
        choices=PostStatus.choices,
        default=PostStatus.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    objects = models.Manager()
    published = PublishedPostManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['published_at']),
            models.Index(fields=['author']),
        ]

    def __str__(self) -> str:
        return self.title

    def is_published(self) -> bool:
        return (
            self.status == PostStatus.PUBLISHED and
            self.published_at and
            self.published_at <= timezone.now()
        )

    def increment_view_count(self) -> None:
        self.view_count = models.F('view_count') + 1
        self.save(update_fields=['view_count'])

    def get_related_posts(self, limit: int = 5):
        return Post.published.filter(
            categories__in=self.categories.all()
        ).exclude(pk=self.pk).distinct()[:limit]


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            status=PostStatus.PUBLISHED,
            published_at__lte=timezone.now()
        )

    def by_author(self, author: User):
        return self.filter(author=author)

    def featured(self):
        return self.filter(is_featured=True)

    def with_categories(self):
        return self.prefetch_related('categories')

    def with_author(self):
        return self.select_related('author')
```