# Existing Codebase

## Schema

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    location VARCHAR(100),
    birth_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
```

## Models

```python
from django.contrib.auth.models import AbstractUser
from django.db import models, connection
from django.db.models import QuerySet
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class UserQuerySet(QuerySet):
    def active(self) -> QuerySet:
        return self.filter(is_active=True)
    
    def by_email_domain(self, domain: str) -> QuerySet:
        return self.filter(email__endswith=f'@{domain}')
    
    def search_by_name(self, query: str) -> QuerySet:
        return self.filter(
            models.Q(first_name__icontains=query) |
            models.Q(last_name__icontains=query)
        )


class UserManager(models.Manager):
    def get_queryset(self) -> UserQuerySet:
        return UserQuerySet(self.model, using=self._db)
    
    def active(self) -> QuerySet:
        return self.get_queryset().active()
    
    def create_user_with_profile(self, username: str, email: str, **kwargs) -> 'User':
        user = self.create(username=username, email=email, **kwargs)
        UserProfile.objects.create(user=user)
        return user


class User(AbstractUser):
    email = models.EmailField(unique=True)
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]
    
    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_profile(self) -> Optional['UserProfile']:
        try:
            return self.profile
        except UserProfile.DoesNotExist:
            return None


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def get_age(self) -> Optional[int]:
        if not self.birth_date:
            return None
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )


class DatabaseHelper:
    @staticmethod
    def execute_query(query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        with connection.cursor() as cursor:
            cursor.execute(query, params or [])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @staticmethod
    def execute_single_query(query: str, params: Optional[List[Any]] = None) -> Optional[Dict[str, Any]]:
        results = DatabaseHelper.execute_query(query, params)
        return results[0] if results else None


# Constants for common queries
USER_SEARCH_FIELDS = ['username', 'first_name', 'last_name', 'email']
DEFAULT_USER_SELECT = """
    SELECT u.id, u.username, u.email, u.first_name, u.last_name, 
           u.is_active, u.date_joined, u.last_login,
           p.bio, p.location, p.birth_date
    FROM users u
    LEFT JOIN user_profiles p ON u.id = p.user_id
"""
```