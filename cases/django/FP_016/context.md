# Existing Codebase

## Schema

```python
# migrations/0001_initial.py
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published')], default='draft', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='blog.category')),
            ],
        ),
    ]
```

## Models

```python
from django.db import models
from django.db.models import QuerySet
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class PostStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'


class CategoryQuerySet(QuerySet['Category']):
    def with_published_posts(self) -> QuerySet['Category']:
        return self.filter(posts__status=PostStatus.PUBLISHED).distinct()
    
    def active(self) -> QuerySet['Category']:
        return self.filter(posts__isnull=False).distinct()


class CategoryManager(models.Manager['Category']):
    def get_queryset(self) -> CategoryQuerySet:
        return CategoryQuerySet(self.model, using=self._db)
    
    def with_published_posts(self) -> CategoryQuerySet:
        return self.get_queryset().with_published_posts()


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = CategoryManager()
    
    if TYPE_CHECKING:
        posts: RelatedManager['Post']
    
    class Meta:
        verbose_name_plural = 'categories'
    
    def __str__(self) -> str:
        return self.name


class PostQuerySet(QuerySet['Post']):
    def published(self) -> QuerySet['Post']:
        return self.filter(status=PostStatus.PUBLISHED)
    
    def drafts(self) -> QuerySet['Post']:
        return self.filter(status=PostStatus.DRAFT)
    
    def by_category(self, category_slug: str) -> QuerySet['Post']:
        return self.filter(category__slug=category_slug)


class PostManager(models.Manager['Post']):
    def get_queryset(self) -> PostQuerySet:
        return PostQuerySet(self.model, using=self._db)
    
    def published(self) -> PostQuerySet:
        return self.get_queryset().published()


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=PostStatus.choices,
        default=PostStatus.DRAFT
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = PostManager()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return self.title
    
    def is_published(self) -> bool:
        return self.status == PostStatus.PUBLISHED
```