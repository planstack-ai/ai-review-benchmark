import re
from typing import Optional
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
    RegexValidator,
    MinValueValidator,
    MaxValueValidator
)
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            MinLengthValidator(3, message='Username must be at least 3 characters long.'),
            MaxLengthValidator(30, message='Username must not exceed 30 characters.'),
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='Username can only contain letters, numbers, and underscores.'
            )
        ]
    )
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': 'A user with this email address already exists.'
        }
    )
    age = models.PositiveIntegerField(
        validators=[
            MinValueValidator(13, message='You must be at least 13 years old.'),
            MaxValueValidator(120, message='Please enter a valid age.')
        ]
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        default='',
        validators=[
            RegexValidator(
                regex=r'^\+?[\d\s\-()]+$',
                message='Please enter a valid phone number format.'
            )
        ]
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        default='',
        validators=[
            MaxLengthValidator(500, message='Bio must not exceed 500 characters.')
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"

    def clean(self) -> None:
        super().clean()

        if self.username:
            if len(self.username) < 3:
                raise ValidationError({
                    'username': 'Username must be at least 3 characters long.'
                })
            if len(self.username) > 30:
                raise ValidationError({
                    'username': 'Username must not exceed 30 characters.'
                })
            if not re.match(r'^[a-zA-Z0-9_]+$', self.username):
                raise ValidationError({
                    'username': 'Username can only contain letters, numbers, and underscores.'
                })

        if self.age is not None:
            if self.age < 13:
                raise ValidationError({
                    'age': 'You must be at least 13 years old to create a profile.'
                })
            if self.age > 120:
                raise ValidationError({
                    'age': 'Please enter a valid age (maximum 120 years).'
                })

        if self.phone:
            cleaned_phone = re.sub(r'[\s\-()]+', '', self.phone)
            if not re.match(r'^\+?\d+$', cleaned_phone):
                raise ValidationError({
                    'phone': 'Please enter a valid phone number containing only digits, spaces, hyphens, and parentheses.'
                })

        if self.bio and len(self.bio) > 500:
            raise ValidationError({
                'bio': 'Bio must not exceed 500 characters.'
            })

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def display_name(self) -> str:
        return self.username or self.email.split('@')[0]
