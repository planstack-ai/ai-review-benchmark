from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from typing import Optional, List, Dict, Any
import re
from datetime import datetime


class User(models.Model):
    email = models.EmailField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'users'


class UserService:
    
    def __init__(self):
        self.model = User
    
    def create_user(self, email: str, first_name: str, last_name: str, 
                   password: str) -> User:
        self._validate_email_format(email)
        self._validate_password_strength(password)
        self._validate_name_fields(first_name, last_name)
        
        with transaction.atomic():
            user = self.model(
                email=email.lower().strip(),
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                password=make_password(password)
            )
            user.full_clean()
            user.save()
            return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        try:
            return self.model.objects.get(email=email.lower().strip())
        except self.model.DoesNotExist:
            return None
    
    def update_user_profile(self, user_id: int, **kwargs) -> User:
        user = self._get_user_by_id(user_id)
        
        allowed_fields = ['first_name', 'last_name', 'email']
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if 'email' in update_data:
            self._validate_email_format(update_data['email'])
            update_data['email'] = update_data['email'].lower().strip()
        
        with transaction.atomic():
            for field, value in update_data.items():
                setattr(user, field, value)
            user.full_clean()
            user.save()
            return user
    
    def deactivate_user(self, user_id: int) -> User:
        user = self._get_user_by_id(user_id)
        user.is_active = False
        user.save(update_fields=['is_active'])
        return user
    
    def get_active_users(self) -> List[User]:
        return list(self.model.objects.filter(is_active=True).order_by('date_joined'))
    
    def _get_user_by_id(self, user_id: int) -> User:
        try:
            return self.model.objects.get(id=user_id)
        except self.model.DoesNotExist:
            raise ValidationError(f"User with id {user_id} does not exist")
    
    def _validate_email_format(self, email: str) -> None:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")
    
    def _validate_password_strength(self, password: str) -> None:
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one digit")
    
    def _validate_name_fields(self, first_name: str, last_name: str) -> None:
        if not first_name or not first_name.strip():
            raise ValidationError("First name is required")
        if not last_name or not last_name.strip():
            raise ValidationError("Last name is required")
        if len(first_name.strip()) > 100:
            raise ValidationError("First name cannot exceed 100 characters")
        if len(last_name.strip()) > 100:
            raise ValidationError("Last name cannot exceed 100 characters")