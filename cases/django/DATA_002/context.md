# Existing Codebase

## Schema

```python
# accounts/migrations/0001_initial.py
from django.db import migrations, models
import django.contrib.auth.models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='superuser status')),
                ('username', models.CharField(max_length=150, unique=True, verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'db_table': 'auth_user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
```

## Models

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from typing import Optional


class UserManager(models.Manager):
    def get_by_email(self, email: str) -> Optional['User']:
        """Get user by email address (case-insensitive)."""
        try:
            return self.get(email__iexact=email)
        except User.DoesNotExist:
            return None
    
    def create_user_with_email(self, email: str, password: str, **extra_fields) -> 'User':
        """Create user with email as primary identifier."""
        if not email:
            raise ValueError('Email address is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    email = models.EmailField(
        _('email address'),
        max_length=254,
        help_text=_('Required. Enter a valid email address.')
    )
    
    objects = UserManager()
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def clean(self) -> None:
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)
    
    def get_display_name(self) -> str:
        """Return the best available display name for the user."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.email:
            return self.email.split('@')[0]
        return self.username
    
    @property
    def has_complete_profile(self) -> bool:
        """Check if user has completed their profile."""
        return bool(self.first_name and self.last_name and self.email)


# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def clean_email(self) -> str:
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError('A user with this email already exists.')
        return email
```