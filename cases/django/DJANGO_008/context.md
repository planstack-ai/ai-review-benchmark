# Existing Codebase

## Schema

```sql
CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254),
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE core_auditlog (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE core_requestmetrics (
    id SERIAL PRIMARY KEY,
    path VARCHAR(500) NOT NULL,
    method VARCHAR(10) NOT NULL,
    response_time_ms INTEGER,
    status_code INTEGER,
    user_id INTEGER REFERENCES auth_user(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Models

```python
from django.contrib.auth.models import User
from django.db import models
from typing import Optional
import uuid


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50)
    resource_type = models.CharField(max_length=100, blank=True)
    resource_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'core_auditlog'
        ordering = ['-timestamp']
    
    def __str__(self) -> str:
        return f"{self.action} by {self.user or 'Anonymous'} at {self.timestamp}"


class RequestMetrics(models.Model):
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    response_time_ms = models.PositiveIntegerField()
    status_code = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'core_requestmetrics'
        ordering = ['-timestamp']
    
    @classmethod
    def record_request(cls, request, response, response_time: float) -> 'RequestMetrics':
        return cls.objects.create(
            path=request.path,
            method=request.method,
            response_time_ms=int(response_time * 1000),
            status_code=response.status_code,
            user=getattr(request, 'user', None) if hasattr(request, 'user') else None
        )


class SecurityEvent(models.Model):
    FAILED_LOGIN = 'failed_login'
    SUSPICIOUS_REQUEST = 'suspicious_request'
    RATE_LIMIT_EXCEEDED = 'rate_limit_exceeded'
    
    EVENT_TYPES = [
        (FAILED_LOGIN, 'Failed Login'),
        (SUSPICIOUS_REQUEST, 'Suspicious Request'),
        (RATE_LIMIT_EXCEEDED, 'Rate Limit Exceeded'),
    ]
    
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    @classmethod
    def log_security_event(cls, event_type: str, ip_address: str, 
                          user_agent: str = '', **details) -> 'SecurityEvent':
        return cls.objects.create(
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
```