# Existing Codebase

## Schema

```sql
CREATE TABLE blog_post (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    author_id INTEGER NOT NULL REFERENCES auth_user(id),
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    view_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE blog_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE blog_post_categories (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES blog_post(id),
    category_id INTEGER NOT NULL REFERENCES blog_category(id),
    UNIQUE(post_id, category_id)
);
```

## Models

```python
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet


class PostStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'


class ActiveCategoryManager(models.Manager['Category']):
    def get_queryset(self) -> 'QuerySet[Category]':
        return super().get_queryset().filter(is_active=True)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    
    objects = models.Manager()
    active = ActiveCategoryManager()
    
    class Meta:
        verbose_name_plural = 'categories'
    
    def __str__(self) -> str:
        return self.name


class PublishedPostManager(models.Manager['Post']):
    def get_queryset(self) -> 'QuerySet[Post]':
        return super().get_queryset().filter(
            status=PostStatus.PUBLISHED,
            created_at__lte=timezone.now()
        )
    
    def featured(self) -> 'QuerySet[Post]':
        return self.get_queryset().filter(is_featured=True)
    
    def by_category(self, category_slug: str) -> 'QuerySet[Post]':
        return self.get_queryset().filter(categories__slug=category_slug)
    
    def recent(self, days: int = 30) -> 'QuerySet[Post]':
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        return self.get_queryset().filter(created_at__gte=cutoff_date)
    
    def popular(self, min_views: int = 100) -> 'QuerySet[Post]':
        return self.get_queryset().filter(view_count__gte=min_views)


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=PostStatus.choices,
        default=PostStatus.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    categories = models.ManyToManyField(Category, related_name='posts', blank=True)
    is_featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    
    objects = models.Manager()
    published = PublishedPostManager()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return self.title
    
    def increment_view_count(self) -> None:
        self.view_count = models.F('view_count') + 1
        self.save(update_fields=['view_count'])
    
    def is_published(self) -> bool:
        return (
            self.status == PostStatus.PUBLISHED and 
            self.created_at <= timezone.now()
        )
```