# Existing Codebase

## Schema

```sql
-- Articles table with denormalized fields for performance
CREATE TABLE articles_article (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER REFERENCES auth_user(id),
    category_id INTEGER REFERENCES articles_category(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Denormalized fields for read performance
    author_name VARCHAR(150),
    category_name VARCHAR(100),
    comment_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    
    INDEX idx_article_category_created (category_id, created_at),
    INDEX idx_article_author_created (author_id, created_at)
);

CREATE TABLE articles_comment (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles_article(id),
    author_id INTEGER REFERENCES auth_user(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Models

```python
from django.db import models
from django.contrib.auth.models import User
from django.db.models import F
from typing import Optional


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "categories"
    
    def __str__(self) -> str:
        return self.name


class ArticleQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)
    
    def by_category(self, category_name: str):
        return self.filter(category_name=category_name)
    
    def popular(self, min_views: int = 100):
        return self.filter(view_count__gte=min_views)


class ArticleManager(models.Manager):
    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)
    
    def published(self):
        return self.get_queryset().published()
    
    def increment_view_count(self, article_id: int) -> None:
        self.filter(id=article_id).update(view_count=F('view_count') + 1)


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    
    # Denormalized fields for read performance
    author_name = models.CharField(max_length=150, blank=True)
    category_name = models.CharField(max_length=100, blank=True)
    comment_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    objects = ArticleManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'created_at']),
            models.Index(fields=['author', 'created_at']),
        ]
    
    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self) -> str:
        return f"/articles/{self.id}/"


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self) -> str:
        return f"Comment by {self.author.username} on {self.article.title}"
```