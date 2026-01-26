from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from django.db import models
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator, Page


class UserActivityManager(models.Manager):
    def for_user(self, user: User, start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None):
        queryset = self.filter(user=user)
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        return queryset.order_by('-created_at')

    def recent(self, page: int = 1, per_page: int = 20) -> Page:
        queryset = self.select_related('user').order_by('-created_at')
        paginator = Paginator(queryset, per_page)
        return paginator.get_page(page)

    def by_action_type(self, action_type: str):
        return self.filter(action_type=action_type).order_by('-created_at')

    def last_n_days(self, days: int):
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date).order_by('-created_at')

    def grouped_by_date(self, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        queryset = self.all()
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        return list(
            queryset
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('-date')
        )

    def unique_action_types(self) -> List[str]:
        return list(
            self.values_list('action_type', flat=True)
            .distinct()
            .order_by('action_type')
        )


class UserActivity(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities',
        db_index=True
    )
    action_type = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = UserActivityManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action_type', 'created_at']),
        ]

    def __str__(self) -> str:
        return f"{self.user.username}: {self.action_type} at {self.created_at}"


class UserActivityService:
    def record_activity(self, user: User, action_type: str,
                        description: str = '', metadata: Optional[Dict[str, Any]] = None,
                        ip_address: Optional[str] = None,
                        user_agent: str = '') -> UserActivity:
        return UserActivity.objects.create(
            user=user,
            action_type=action_type,
            description=description,
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent
        )

    def bulk_record_activities(self, activities_data: List[Dict[str, Any]]) -> List[UserActivity]:
        activities = []
        for data in activities_data:
            activity = UserActivity(
                user=data['user'],
                action_type=data['action_type'],
                description=data.get('description', ''),
                metadata=data.get('metadata', {}),
                ip_address=data.get('ip_address'),
                user_agent=data.get('user_agent', '')
            )
            activities.append(activity)

        return UserActivity.objects.bulk_create(activities)

    def get_user_activities(self, user: User, start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None):
        return UserActivity.objects.for_user(user, start_date, end_date)

    def get_recent_activities(self, page: int = 1, per_page: int = 20) -> Page:
        return UserActivity.objects.recent(page, per_page)

    def filter_by_action_type(self, action_type: str):
        return UserActivity.objects.by_action_type(action_type)

    def get_activity_count(self, user: Optional[User] = None,
                           action_type: Optional[str] = None) -> int:
        queryset = UserActivity.objects.all()
        if user:
            queryset = queryset.filter(user=user)
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        return queryset.count()

    def get_activities_last_n_days(self, days: int):
        return UserActivity.objects.last_n_days(days)

    def get_unique_action_types(self) -> List[str]:
        return UserActivity.objects.unique_action_types()

    def get_activities_grouped_by_date(self, start_date: Optional[datetime] = None,
                                       end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        return UserActivity.objects.grouped_by_date(start_date, end_date)
