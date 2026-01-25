# Existing Codebase

## Schema

```sql
CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE TABLE accounts_userprofile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES auth_user(id),
    bio TEXT,
    avatar VARCHAR(100),
    email_verified BOOLEAN NOT NULL DEFAULT false,
    welcome_email_sent BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

## Models

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet


class User(AbstractUser):
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class UserProfileManager(models.Manager['UserProfile']):
    def get_queryset(self) -> 'QuerySet[UserProfile]':
        return super().get_queryset().select_related('user')
    
    def verified_users(self) -> 'QuerySet[UserProfile]':
        return self.filter(email_verified=True)
    
    def pending_welcome_emails(self) -> 'QuerySet[UserProfile]':
        return self.filter(
            welcome_email_sent=False,
            user__is_active=True
        )


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    email_verified = models.BooleanField(default=False)
    welcome_email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserProfileManager()
    
    class Meta:
        db_table = 'accounts_userprofile'
    
    def __str__(self) -> str:
        return f"{self.user.email}'s profile"
    
    def mark_welcome_email_sent(self) -> None:
        self.welcome_email_sent = True
        self.save(update_fields=['welcome_email_sent'])


@receiver(post_save, sender=User)
def create_user_profile(sender, instance: User, created: bool, **kwargs) -> None:
    if created:
        UserProfile.objects.create(user=instance)
```

```python
# emails/services.py
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from accounts.models import User


class EmailService:
    @staticmethod
    def send_welcome_email(user: 'User') -> bool:
        try:
            subject = f"Welcome to {settings.SITE_NAME}, {user.first_name}!"
            html_message = render_to_string('emails/welcome.html', {
                'user': user,
                'site_name': settings.SITE_NAME,
            })
            
            send_mail(
                subject=subject,
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception:
            return False
```