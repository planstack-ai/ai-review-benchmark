from typing import List, Optional, Dict, Any
from django.db import transaction
from django.db.models import Q, QuerySet
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime

from .models import Article, Category, Tag


class ArticleService:
    """Service class for managing article operations with soft delete support."""
    
    def __init__(self):
        self.model = Article
    
    def get_published_articles(self, category_id: Optional[int] = None) -> QuerySet:
        """Retrieve all published articles, optionally filtered by category."""
        queryset = self.model.objects.filter(
            is_published=True,
            published_at__lte=timezone.now()
        )
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        return queryset.order_by('-published_at')
    
    def search_articles(self, query: str, category_ids: Optional[List[int]] = None) -> QuerySet:
        """Search articles by title and content."""
        if not query.strip():
            return self.model.objects.none()
        
        search_filter = Q(title__icontains=query) | Q(content__icontains=query)
        queryset = self.model.objects.filter(search_filter)
        
        if category_ids:
            queryset = queryset.filter(category_id__in=category_ids)
        
        return queryset.order_by('-created_at')
    
    def get_article_by_slug(self, slug: str) -> Optional[Article]:
        """Retrieve a single article by its slug."""
        try:
            return self.model.objects.get(slug=slug, is_published=True)
        except Article.DoesNotExist:
            return None
    
    def get_articles_by_author(self, author_id: int) -> QuerySet:
        """Get all articles by a specific author."""
        return self.model.objects.filter(
            author_id=author_id,
            deleted_at__isnull=True
        ).order_by('-created_at')
    
    def get_recent_articles(self, limit: int = 10) -> QuerySet:
        """Get recently published articles."""
        return self.model.objects.filter(
            is_published=True,
            published_at__lte=timezone.now(),
            deleted_at__isnull=True
        ).order_by('-published_at')[:limit]
    
    @transaction.atomic
    def create_article(self, article_data: Dict[str, Any]) -> Article:
        """Create a new article with validation."""
        self._validate_article_data(article_data)
        
        article = self.model(**article_data)
        article.slug = self._generate_unique_slug(article.title)
        article.save()
        
        return article
    
    @transaction.atomic
    def update_article(self, article_id: int, update_data: Dict[str, Any]) -> Optional[Article]:
        """Update an existing article."""
        try:
            article = self.model.objects.get(id=article_id, deleted_at__isnull=True)
            
            for field, value in update_data.items():
                if hasattr(article, field):
                    setattr(article, field, value)
            
            if 'title' in update_data:
                article.slug = self._generate_unique_slug(update_data['title'])
            
            article.updated_at = timezone.now()
            article.save()
            
            return article
        except Article.DoesNotExist:
            return None
    
    def soft_delete_article(self, article_id: int) -> bool:
        """Soft delete an article by setting deleted_at timestamp."""
        try:
            article = self.model.objects.get(id=article_id, deleted_at__isnull=True)
            article.deleted_at = timezone.now()
            article.save()
            return True
        except Article.DoesNotExist:
            return False
    
    def _validate_article_data(self, data: Dict[str, Any]) -> None:
        """Validate article data before creation."""
        required_fields = ['title', 'content', 'author_id', 'category_id']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(f"Field '{field}' is required")
        
        if len(data['title']) > 200:
            raise ValidationError("Title cannot exceed 200 characters")
    
    def _generate_unique_slug(self, title: str) -> str:
        """Generate a unique slug from the article title."""
        base_slug = title.lower().replace(' ', '-').replace('_', '-')
        base_slug = ''.join(c for c in base_slug if c.isalnum() or c == '-')
        
        slug = base_slug
        counter = 1
        
        while self.model.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug