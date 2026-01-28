# Existing Codebase

## Schema

```sql
CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE
);

CREATE TABLE accounts_role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    permissions TEXT[],
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE accounts_userrole (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    role_id INTEGER REFERENCES accounts_role(id),
    organization_id INTEGER,
    granted_at TIMESTAMP DEFAULT NOW(),
    granted_by_id INTEGER REFERENCES auth_user(id)
);

CREATE TABLE projects_project (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    organization_id INTEGER NOT NULL,
    owner_id INTEGER REFERENCES auth_user(id),
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Models

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import QuerySet
from typing import List, Optional


class RoleQuerySet(QuerySet):
    def active(self):
        return self.filter(is_active=True)
    
    def with_permission(self, permission: str):
        return self.filter(permissions__contains=[permission])


class Role(models.Model):
    ADMIN = 'admin'
    MANAGER = 'manager'
    DEVELOPER = 'developer'
    VIEWER = 'viewer'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrator'),
        (MANAGER, 'Project Manager'),
        (DEVELOPER, 'Developer'),
        (VIEWER, 'Viewer'),
    ]
    
    name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)
    permissions = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    
    objects = RoleQuerySet.as_manager()
    
    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions
    
    class Meta:
        db_table = 'accounts_role'


class UserRoleQuerySet(QuerySet):
    def for_user(self, user_id: int):
        return self.filter(user_id=user_id)
    
    def for_organization(self, org_id: int):
        return self.filter(organization_id=org_id)
    
    def active_roles(self):
        return self.select_related('role').filter(role__is_active=True)


class UserRole(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    organization_id = models.IntegerField()
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, 
                                   null=True, related_name='granted_roles')
    
    objects = UserRoleQuerySet.as_manager()
    
    class Meta:
        db_table = 'accounts_userrole'
        unique_together = ['user', 'role', 'organization_id']


class ProjectQuerySet(QuerySet):
    def for_organization(self, org_id: int):
        return self.filter(organization_id=org_id)
    
    def public(self):
        return self.filter(is_public=True)
    
    def accessible_by_user(self, user_id: int):
        return self.filter(
            models.Q(is_public=True) | 
            models.Q(owner_id=user_id)
        )


class Project(models.Model):
    name = models.CharField(max_length=200)
    organization_id = models.IntegerField()
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = ProjectQuerySet.as_manager()
    
    class Meta:
        db_table = 'projects_project'


# Permission constants
class Permissions:
    PROJECT_CREATE = 'project.create'
    PROJECT_READ = 'project.read'
    PROJECT_UPDATE = 'project.update'
    PROJECT_DELETE = 'project.delete'
    USER_MANAGE = 'user.manage'
    ROLE_ASSIGN = 'role.assign'
```