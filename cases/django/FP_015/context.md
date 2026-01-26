# Existing Codebase

## Schema

```sql
CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INTEGER REFERENCES authors(id),
    publication_date DATE,
    isbn VARCHAR(13) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

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
from django.db.models import Prefetch, Q
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class AuthorQuerySet(models.QuerySet["Author"]):
    def with_books(self) -> "QuerySet[Author]":
        return self.prefetch_related("books")
    
    def with_books_and_reviews(self) -> "QuerySet[Author]":
        return self.prefetch_related(
            Prefetch(
                "books",
                queryset=Book.objects.select_related("author").prefetch_related("reviews")
            )
        )
    
    def active(self) -> "QuerySet[Author]":
        return self.filter(books__isnull=False).distinct()


class AuthorManager(models.Manager["Author"]):
    def get_queryset(self) -> AuthorQuerySet:
        return AuthorQuerySet(self.model, using=self._db)
    
    def with_books(self) -> "QuerySet[Author]":
        return self.get_queryset().with_books()
    
    def with_books_and_reviews(self) -> "QuerySet[Author]":
        return self.get_queryset().with_books_and_reviews()


class Author(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = AuthorManager()
    
    class Meta:
        ordering = ["name"]
    
    def __str__(self) -> str:
        return self.name
    
    @property
    def book_count(self) -> int:
        return self.books.count()


class BookQuerySet(models.QuerySet["Book"]):
    def with_author(self) -> "QuerySet[Book]":
        return self.select_related("author")
    
    def with_reviews(self) -> "QuerySet[Book]":
        return self.prefetch_related("reviews")
    
    def with_author_and_reviews(self) -> "QuerySet[Book]":
        return self.select_related("author").prefetch_related("reviews")
    
    def published(self) -> "QuerySet[Book]":
        return self.filter(publication_date__isnull=False)


class BookManager(models.Manager["Book"]):
    def get_queryset(self) -> BookQuerySet:
        return BookQuerySet(self.model, using=self._db)
    
    def with_author(self) -> "QuerySet[Book]":
        return self.get_queryset().with_author()
    
    def with_reviews(self) -> "QuerySet[Book]":
        return self.get_queryset().with_reviews()


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    publication_date = models.DateField(null=True, blank=True)
    isbn = models.CharField(max_length=13, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = BookManager()
    
    class Meta:
        ordering = ["-publication_date", "title"]
    
    def __str__(self) -> str:
        return self.title
    
    @property
    def review_count(self) -> int:
        return self.reviews.count()
    
    @property
    def average_rating(self) -> float:
        reviews = self.reviews.all()
        if not reviews:
            return 0.0
        return sum(review.rating for review in reviews) / len(reviews)


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    reviewer_name = models.CharField(max_length=255)
    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self) -> str:
        return f"{self.book.title} - {self.rating}/5"
```