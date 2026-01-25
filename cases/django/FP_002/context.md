# Existing Codebase

## Schema

```python
# migrations/0001_initial.py
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    initial = True
    
    dependencies = []
    
    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('username', models.CharField(max_length=150, unique=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('age', models.PositiveIntegerField()),
                ('phone', models.CharField(max_length=15, blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
```

## Models

```python
# models.py
from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from typing import Any


class UserManager(models.Manager):
    def active_users(self):
        return self.filter(is_active=True)
    
    def by_age_range(self, min_age: int, max_age: int):
        return self.filter(age__gte=min_age, age__lte=max_age)


class User(models.Model):
    email = models.EmailField(unique=True, max_length=254)
    username = models.CharField(
        max_length=150, 
        unique=True,
        validators=[
            MinLengthValidator(3),
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='Username can only contain letters, numbers, and underscores.'
            )
        ]
    )
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    age = models.PositiveIntegerField()
    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.username} ({self.email})"
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
    
    def clean(self) -> None:
        super().clean()
        if self.age and self.age < 13:
            raise ValidationError({'age': 'Users must be at least 13 years old.'})
        
        if self.phone and not self.phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValidationError({'phone': 'Phone number must contain only digits, spaces, hyphens, and plus signs.'})
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


# constants.py
MIN_USER_AGE = 13
MAX_USER_AGE = 120
PHONE_REGEX = r'^\+?[\d\s\-]+$'
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 150
```