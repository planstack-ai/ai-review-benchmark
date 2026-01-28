# Existing Codebase

## Schema

```sql
CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254),
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP DEFAULT NOW()
);

CREATE TABLE core_document (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    author_id INTEGER REFERENCES auth_user(id),
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE core_documentvalidation (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES core_document(id),
    validator_id INTEGER REFERENCES auth_user(id),
    validation_type VARCHAR(50) NOT NULL,
    is_valid BOOLEAN DEFAULT FALSE,
    validated_at TIMESTAMP DEFAULT NOW()
);
```

## Models

```python
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from typing import Optional


class DocumentStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PENDING = 'pending', 'Pending Review'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class DocumentQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=DocumentStatus.APPROVED)
    
    def pending_validation(self):
        return self.filter(status=DocumentStatus.PENDING)
    
    def by_author(self, user: User):
        return self.filter(author=user)


class DocumentManager(models.Manager):
    def get_queryset(self):
        return DocumentQuerySet(self.model, using=self._db)
    
    def published(self):
        return self.get_queryset().published()
    
    def create_draft(self, title: str, content: str, author: User) -> 'Document':
        return self.create(
            title=title,
            content=content,
            author=author,
            status=DocumentStatus.DRAFT
        )


class Document(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = DocumentManager()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return self.title
    
    def can_be_validated(self) -> bool:
        return self.status in [DocumentStatus.DRAFT, DocumentStatus.PENDING]
    
    def is_published(self) -> bool:
        return self.status == DocumentStatus.APPROVED


class ValidationTypeChoices(models.TextChoices):
    CONTENT = 'content', 'Content Review'
    TECHNICAL = 'technical', 'Technical Review'
    COMPLIANCE = 'compliance', 'Compliance Check'
    ADMIN_BYPASS = 'admin_bypass', 'Administrative Bypass'


class DocumentValidation(models.Model):
    document = models.ForeignKey(
        Document, 
        on_delete=models.CASCADE, 
        related_name='validations'
    )
    validator = models.ForeignKey(User, on_delete=models.CASCADE)
    validation_type = models.CharField(
        max_length=50,
        choices=ValidationTypeChoices.choices
    )
    is_valid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    validated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['document', 'validation_type']
        ordering = ['-validated_at']
    
    def __str__(self) -> str:
        return f"{self.document.title} - {self.get_validation_type_display()}"


# Constants for admin operations
ADMIN_BYPASS_PERMISSIONS = ['core.bypass_validation', 'core.admin_override']
TESTING_USER_PREFIX = 'test_'
VALIDATION_EXEMPT_STATUSES = [DocumentStatus.APPROVED, DocumentStatus.REJECTED]
```