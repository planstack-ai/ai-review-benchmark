# Existing Codebase

## Schema

```sql
-- Authors table
CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    bio TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Books table
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    isbn VARCHAR(13) UNIQUE NOT NULL,
    author_id INTEGER REFERENCES authors(id),
    publisher_id INTEGER REFERENCES publishers(id),
    publication_date DATE,
    page_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Publishers table
CREATE TABLE publishers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    website VARCHAR(255)
);

-- Reviews table
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES books(id),
    reviewer_name VARCHAR(255) NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Models

```python
from django.db import models
from django.db.models import Avg, Count, Prefetch
from typing import Optional


class AuthorManager(models.Manager):
    def with_book_count(self):
        return self.annotate(book_count=Count('books'))
    
    def active_authors(self):
        return self.filter(books__isnull=False).distinct()


class Author(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = AuthorManager()
    
    class Meta:
        ordering = ['name']
    
    def __str__(self) -> str:
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    
    def __str__(self) -> str:
        return self.name


class BookQuerySet(models.QuerySet):
    def published(self):
        return self.filter(publication_date__isnull=False)
    
    def by_author(self, author_id: int):
        return self.filter(author_id=author_id)
    
    def with_avg_rating(self):
        return self.annotate(avg_rating=Avg('reviews__rating'))
    
    def recent_books(self, days: int = 30):
        from django.utils import timezone
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(created_at__gte=cutoff)


class BookManager(models.Manager):
    def get_queryset(self):
        return BookQuerySet(self.model, using=self._db)
    
    def published(self):
        return self.get_queryset().published()
    
    def with_details(self):
        return self.select_related('author', 'publisher')


class Book(models.Model):
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='books')
    publication_date = models.DateField(null=True, blank=True)
    page_count = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = BookManager()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return self.title
    
    @property
    def is_published(self) -> bool:
        return self.publication_date is not None


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=255)
    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.reviewer_name} - {self.rating}/5"


# Constants
BOOKS_PER_PAGE = 20
MAX_RECENT_REVIEWS = 5
DEFAULT_RATING_THRESHOLD = 3.5
```