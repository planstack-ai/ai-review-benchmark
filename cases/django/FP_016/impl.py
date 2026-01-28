from typing import Optional, Dict, Any
from django.db import transaction, models
from django.core.cache import cache
from django.db.models import F
from django.utils import timezone
from decimal import Decimal


class CounterCacheService:
    
    def __init__(self, model_class: models.Model):
        self.model_class = model_class
        self.cache_timeout = 3600
        
    def get_cached_count(self, filter_params: Optional[Dict[str, Any]] = None) -> int:
        cache_key = self._generate_cache_key(filter_params)
        cached_value = cache.get(cache_key)
        
        if cached_value is not None:
            return cached_value
            
        count = self._calculate_fresh_count(filter_params)
        cache.set(cache_key, count, self.cache_timeout)
        return count
        
    def increment_counter(self, filter_params: Optional[Dict[str, Any]] = None, 
                         increment_by: int = 1) -> None:
        cache_key = self._generate_cache_key(filter_params)
        
        with transaction.atomic():
            current_count = cache.get(cache_key)
            if current_count is not None:
                new_count = current_count + increment_by
                cache.set(cache_key, new_count, self.cache_timeout)
            else:
                self._refresh_cache_entry(filter_params)
                
    def decrement_counter(self, filter_params: Optional[Dict[str, Any]] = None,
                         decrement_by: int = 1) -> None:
        cache_key = self._generate_cache_key(filter_params)
        
        with transaction.atomic():
            current_count = cache.get(cache_key)
            if current_count is not None:
                new_count = max(0, current_count - decrement_by)
                cache.set(cache_key, new_count, self.cache_timeout)
            else:
                self._refresh_cache_entry(filter_params)
                
    def invalidate_cache(self, filter_params: Optional[Dict[str, Any]] = None) -> None:
        cache_key = self._generate_cache_key(filter_params)
        cache.delete(cache_key)
        
    def refresh_all_counters(self) -> Dict[str, int]:
        common_filters = [
            None,
            {'is_active': True},
            {'created_at__gte': timezone.now().replace(hour=0, minute=0, second=0)}
        ]
        
        results = {}
        for filter_params in common_filters:
            cache_key = self._generate_cache_key(filter_params)
            count = self._calculate_fresh_count(filter_params)
            cache.set(cache_key, count, self.cache_timeout)
            results[cache_key] = count
            
        return results
        
    def _generate_cache_key(self, filter_params: Optional[Dict[str, Any]]) -> str:
        model_name = self.model_class._meta.label_lower
        if not filter_params:
            return f"counter_cache:{model_name}:all"
            
        sorted_params = sorted(filter_params.items())
        param_string = "_".join([f"{k}:{v}" for k, v in sorted_params])
        return f"counter_cache:{model_name}:{param_string}"
        
    def _calculate_fresh_count(self, filter_params: Optional[Dict[str, Any]]) -> int:
        queryset = self.model_class.objects.all()
        if filter_params:
            queryset = queryset.filter(**filter_params)
        return queryset.count()
        
    def _refresh_cache_entry(self, filter_params: Optional[Dict[str, Any]]) -> None:
        cache_key = self._generate_cache_key(filter_params)
        fresh_count = self._calculate_fresh_count(filter_params)
        cache.set(cache_key, fresh_count, self.cache_timeout)