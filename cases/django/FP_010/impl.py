from typing import List, Optional, Dict, Any
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone
from myapp.models import Project, CodeReview, ReviewPermission


class CodeReviewAuthorizationService:
    
    ROLE_VIEWER = 'viewer'
    ROLE_REVIEWER = 'reviewer'
    ROLE_ADMIN = 'admin'
    ROLE_OWNER = 'owner'
    
    ROLE_HIERARCHY = {
        ROLE_VIEWER: 1,
        ROLE_REVIEWER: 2,
        ROLE_ADMIN: 3,
        ROLE_OWNER: 4
    }
    
    def __init__(self):
        self.permission_cache = {}
    
    def can_view_review(self, user: User, review: CodeReview) -> bool:
        if not user.is_authenticated:
            return False
        
        user_role = self._get_user_role(user, review.project)
        return user_role is not None
    
    def can_create_review(self, user: User, project: Project) -> bool:
        if not user.is_authenticated:
            return False
        
        user_role = self._get_user_role(user, project)
        required_level = self.ROLE_HIERARCHY.get(self.ROLE_REVIEWER, 0)
        user_level = self.ROLE_HIERARCHY.get(user_role, 0)
        
        return user_level >= required_level
    
    def can_approve_review(self, user: User, review: CodeReview) -> bool:
        if not user.is_authenticated:
            return False
        
        if review.author == user:
            return False
        
        user_role = self._get_user_role(user, review.project)
        required_level = self.ROLE_HIERARCHY.get(self.ROLE_REVIEWER, 0)
        user_level = self.ROLE_HIERARCHY.get(user_role, 0)
        
        return user_level >= required_level
    
    def can_delete_review(self, user: User, review: CodeReview) -> bool:
        if not user.is_authenticated:
            return False
        
        if review.author == user:
            return True
        
        user_role = self._get_user_role(user, review.project)
        required_level = self.ROLE_HIERARCHY.get(self.ROLE_ADMIN, 0)
        user_level = self.ROLE_HIERARCHY.get(user_role, 0)
        
        return user_level >= required_level
    
    def get_accessible_projects(self, user: User) -> List[Project]:
        if not user.is_authenticated:
            return []
        
        permissions = ReviewPermission.objects.filter(user=user).select_related('project')
        return [perm.project for perm in permissions]
    
    @transaction.atomic
    def grant_permission(self, admin_user: User, target_user: User, 
                        project: Project, role: str) -> bool:
        if not self._can_manage_permissions(admin_user, project):
            raise PermissionDenied("Insufficient permissions to grant access")
        
        if role not in self.ROLE_HIERARCHY:
            raise ValueError(f"Invalid role: {role}")
        
        permission, created = ReviewPermission.objects.get_or_create(
            user=target_user,
            project=project,
            defaults={'role': role, 'granted_by': admin_user, 'granted_at': timezone.now()}
        )
        
        if not created:
            permission.role = role
            permission.granted_by = admin_user
            permission.granted_at = timezone.now()
            permission.save()
        
        self._clear_permission_cache(target_user, project)
        return created
    
    def _get_user_role(self, user: User, project: Project) -> Optional[str]:
        cache_key = f"{user.id}_{project.id}"
        
        if cache_key in self.permission_cache:
            return self.permission_cache[cache_key]
        
        if project.owner == user:
            role = self.ROLE_OWNER
        else:
            try:
                permission = ReviewPermission.objects.get(user=user, project=project)
                role = permission.role
            except ReviewPermission.DoesNotExist:
                role = None
        
        self.permission_cache[cache_key] = role
        return role
    
    def _can_manage_permissions(self, user: User, project: Project) -> bool:
        user_role = self._get_user_role(user, project)
        required_level = self.ROLE_HIERARCHY.get(self.ROLE_ADMIN, 0)
        user_level = self.ROLE_HIERARCHY.get(user_role, 0)
        
        return user_level >= required_level
    
    def _clear_permission_cache(self, user: User, project: Project) -> None:
        cache_key = f"{user.id}_{project.id}"
        self.permission_cache.pop(cache_key, None)