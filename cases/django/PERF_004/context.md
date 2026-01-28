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
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE blog_comment (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES blog_post(id),
    author_id INTEGER NOT NULL REFERENCES auth_user(id),
    content TEXT NOT NULL,
    is_approved BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_blog_post_status ON blog_post(status);
CREATE INDEX idx_blog_post_author ON blog_post(author_id);
CREATE INDEX idx_blog_comment_post ON blog_comment(post_id);
CREATE INDEX idx_blog_comment_approved ON blog_comment(is_approved);
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
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class PostQuerySet(models.QuerySet["Post"]):
    def published(self) -> "QuerySet[Post]":
        return self.filter(status=PostStatus.PUBLISHED)
    
    def by_author(self, author: User) -> "QuerySet[Post]":
        return self.filter(author=author)
    
    def recent(self, days: int = 30) -> "QuerySet[Post]":
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(created_at__gte=cutoff)


class PostManager(models.Manager["Post"]):
    def get_queryset(self) -> PostQuerySet:
        return PostQuerySet(self.model, using=self._db)
    
    def published(self) -> PostQuerySet:
        return self.get_queryset().published()


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    status = models.CharField(
        max_length=20,
        choices=PostStatus.choices,
        default=PostStatus.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = PostManager()
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["author"]),
        ]
    
    def __str__(self) -> str:
        return self.title


class CommentQuerySet(models.QuerySet["Comment"]):
    def approved(self) -> "QuerySet[Comment]":
        return self.filter(is_approved=True)
    
    def for_post(self, post: Post) -> "QuerySet[Comment]":
        return self.filter(post=post)


class CommentManager(models.Manager["Comment"]):
    def get_queryset(self) -> CommentQuerySet:
        return CommentQuerySet(self.model, using=self._db)
    
    def approved(self) -> CommentQuerySet:
        return self.get_queryset().approved()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = CommentManager()
    
    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["post"]),
            models.Index(fields=["is_approved"]),
        ]
    
    def __str__(self) -> str:
        return f"Comment by {self.author.username} on {self.post.title}"
```