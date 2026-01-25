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
    publication_date DATE,
    author_id INTEGER REFERENCES authors(id),
    publisher_id INTEGER REFERENCES publishers(id),
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
from django.db.models import QuerySet, Prefetch
from typing import Optional


class AuthorQuerySet(QuerySet):
    def with_book_count(self) -> QuerySet:
        return self.annotate(book_count=models.Count('books'))
    
    def published_authors(self) -> QuerySet:
        return self.filter(books__isnull=False).distinct()


class AuthorManager(models.Manager):
    def get_queryset(self) -> AuthorQuerySet:
        return AuthorQuerySet(self.model, using=self._db)
    
    def with_book_count(self) -> QuerySet:
        return self.get_queryset().with_book_count()


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
    
    class Meta:
        ordering = ['name']
    
    def __str__(self) -> str:
        return self.name


class BookQuerySet(QuerySet):
    def published(self) -> QuerySet:
        return self.filter(publication_date__isnull=False)
    
    def by_author(self, author_id: int) -> QuerySet:
        return self.filter(author_id=author_id)
    
    def with_high_ratings(self, min_rating: int = 4) -> QuerySet:
        return self.filter(reviews__rating__gte=min_rating).distinct()


class BookManager(models.Manager):
    def get_queryset(self) -> BookQuerySet:
        return BookQuerySet(self.model, using=self._db)
    
    def published(self) -> QuerySet:
        return self.get_queryset().published()


class Book(models.Model):
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    publication_date = models.DateField(null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='books')
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = BookManager()
    
    class Meta:
        ordering = ['-publication_date', 'title']
    
    def __str__(self) -> str:
        return self.title
    
    @property
    def average_rating(self) -> Optional[float]:
        ratings = self.reviews.values_list('rating', flat=True)
        return sum(ratings) / len(ratings) if ratings else None


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
        unique_together = ['book', 'reviewer_name']
    
    def __str__(self) -> str:
        return f"{self.reviewer_name} - {self.book.title} ({self.rating}/5)"
```