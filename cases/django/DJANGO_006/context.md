# Existing Codebase

## Schema

```sql
CREATE TABLE auth_user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254),
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_profile (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    bio TEXT,
    avatar VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_posts (
    id INTEGER PRIMARY KEY,
    author_id INTEGER REFERENCES auth_user(id),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    is_published BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Models

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from typing import Optional


class User(AbstractUser):
    email = models.EmailField(unique=True)
    
    def get_absolute_url(self) -> str:
        return reverse('user:profile', kwargs={'username': self.username})


class UserProfileManager(models.Manager):
    def get_for_user(self, user: User) -> Optional['UserProfile']:
        try:
            return self.get(user=user)
        except UserProfile.DoesNotExist:
            return None


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserProfileManager()
    
    def __str__(self) -> str:
        return f"{self.user.username}'s Profile"
    
    def get_absolute_url(self) -> str:
        return self.user.get_absolute_url()


class PostManager(models.Manager):
    def published(self):
        return self.filter(is_published=True)
    
    def by_author(self, author: User):
        return self.filter(author=author)


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = PostManager()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self) -> str:
        return reverse('posts:detail', kwargs={'pk': self.pk})
```

```python
# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserProfile, Post


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio', 'avatar')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 'is_published')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 8}),
        }
```