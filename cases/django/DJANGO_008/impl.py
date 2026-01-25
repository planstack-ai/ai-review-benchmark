from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class PermissionMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        if self._should_skip_permission_check(request):
            return None
        
        if not self._has_required_permissions(request):
            logger.warning(f"Permission denied for path: {request.path}")
            raise PermissionDenied("Insufficient permissions")
        
        return None

    def _should_skip_permission_check(self, request: HttpRequest) -> bool:
        exempt_paths = [
            '/admin/login/',
            '/api/health/',
            '/static/',
            '/media/',
        ]
        return any(request.path.startswith(path) for path in exempt_paths)

    def _has_required_permissions(self, request: HttpRequest) -> bool:
        if request.method == 'GET' and self._is_public_endpoint(request):
            return True
        
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        
        required_perms = self._get_required_permissions(request)
        return self._check_user_permissions(user, required_perms)

    def _is_public_endpoint(self, request: HttpRequest) -> bool:
        public_endpoints = [
            '/api/public/',
            '/docs/',
            '/health/',
        ]
        return any(request.path.startswith(endpoint) for endpoint in public_endpoints)

    def _get_required_permissions(self, request: HttpRequest) -> List[str]:
        path_permissions = {
            '/api/admin/': ['admin.view_user', 'admin.change_user'],
            '/api/reports/': ['reports.view_report'],
            '/api/users/': ['auth.view_user'],
        }
        
        for path, perms in path_permissions.items():
            if request.path.startswith(path):
                return perms
        
        return ['auth.view_user'] if request.method in ['POST', 'PUT', 'DELETE'] else []

    def _check_user_permissions(self, user: User, required_perms: List[str]) -> bool:
        if user.is_superuser:
            return True
        
        for perm in required_perms:
            if not user.has_perm(perm):
                return False
        
        return True

class CodeReviewBenchmarkService:
    def __init__(self):
        self.middleware_config = self._get_middleware_configuration()

    def _get_middleware_configuration(self) -> Dict[str, Any]:
        return {
            'middleware_classes': [
                'django.middleware.security.SecurityMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'myapp.middleware.PermissionMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
                'django.middleware.clickjacking.XFrameOptionsMiddleware',
            ],
            'permission_settings': {
                'strict_mode': True,
                'log_violations': True,
            }
        }

    def validate_middleware_setup(self) -> bool:
        middleware_classes = self.middleware_config.get('middleware_classes', [])
        return len(middleware_classes) > 0 and self._verify_security_middleware(middleware_classes)

    def _verify_security_middleware(self, middleware_classes: List[str]) -> bool:
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ]
        return all(mw in middleware_classes for mw in required_middleware)