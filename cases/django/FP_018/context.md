# Existing Codebase

## Schema

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    is_active BOOLEAN DEFAULT true,
    featured BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES categories(id),
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0
);

CREATE INDEX idx_products_category_active ON products(category_id, is_active);
CREATE INDEX idx_products_featured ON products(featured) WHERE featured = true;
CREATE INDEX idx_categories_parent ON categories(parent_id);
```

## Models

```python
from django.db import models
from django.core.cache import cache
from django.conf import settings
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class CategoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)
    
    def root_categories(self):
        return self.filter(parent_id__isnull=True)
    
    def with_products(self):
        return self.filter(products__is_active=True).distinct()

class CategoryManager(models.Manager):
    def get_queryset(self):
        return CategoryQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def get_navigation_tree(self) -> List[dict]:
        cache_key = "category_navigation_tree"
        cached_tree = cache.get(cache_key)
        if cached_tree is not None:
            return cached_tree
        
        categories = self.active().order_by('sort_order', 'name')
        tree = self._build_tree(categories)
        cache.set(cache_key, tree, timeout=3600)
        return tree
    
    def _build_tree(self, categories):
        tree = []
        category_dict = {cat.id: cat for cat in categories}
        
        for category in categories:
            if category.parent_id is None:
                tree.append({
                    'id': category.id,
                    'name': category.name,
                    'slug': category.slug,
                    'children': []
                })
        
        return tree

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    objects = CategoryManager()
    
    class Meta:
        verbose_name_plural = "categories"
        ordering = ['sort_order', 'name']

class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)
    
    def featured(self):
        return self.filter(featured=True)
    
    def by_category(self, category_slug: str):
        return self.filter(category__slug=category_slug, category__is_active=True)

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def get_featured_products(self, limit: int = 10) -> List['Product']:
        cache_key = f"featured_products_{limit}"
        cached_products = cache.get(cache_key)
        if cached_products is not None:
            return cached_products
        
        products = list(
            self.active()
            .featured()
            .select_related('category')
            .order_by('-created_at')[:limit]
        )
        cache.set(cache_key, products, timeout=1800)
        return products

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ProductManager()
    
    class Meta:
        ordering = ['-created_at']
    
    @property
    def cache_key(self) -> str:
        return f"product_{self.slug}"
    
    def invalidate_cache(self):
        cache.delete(self.cache_key)
        cache.delete("featured_products_10")
        cache.delete("category_navigation_tree")

# Cache configuration constants
CACHE_TIMEOUTS = {
    'product_detail': 3600,
    'category_tree': 3600,
    'featured_products': 1800,
    'product_list': 900,
}

CACHE_KEYS = {
    'navigation': 'category_navigation_tree',
    'featured': 'featured_products_{limit}',
    'category_products': 'category_products_{slug}_{page}',
}
```