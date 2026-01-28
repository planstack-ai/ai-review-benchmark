from typing import List, Dict, Any, Optional
from django.core.cache import cache
from django.conf import settings
from django.db import models
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class CacheWarmingService:
    
    def __init__(self, cache_timeout: int = 3600):
        self.cache_timeout = cache_timeout
        self.batch_size = getattr(settings, 'CACHE_WARMING_BATCH_SIZE', 100)
        
    def warm_all_caches(self) -> Dict[str, bool]:
        results = {}
        
        results['user_profiles'] = self._warm_user_profile_cache()
        results['popular_repositories'] = self._warm_repository_cache()
        results['benchmark_metrics'] = self._warm_benchmark_metrics_cache()
        results['leaderboard'] = self._warm_leaderboard_cache()
        
        return results
    
    def _warm_user_profile_cache(self) -> bool:
        try:
            from apps.users.models import UserProfile
            
            active_users = UserProfile.objects.filter(
                is_active=True,
                last_login__gte=timezone.now() - timezone.timedelta(days=30)
            ).select_related('user')[:self.batch_size]
            
            cached_count = 0
            for profile in active_users:
                cache_key = f"user_profile:{profile.user.id}"
                profile_data = {
                    'username': profile.user.username,
                    'email': profile.user.email,
                    'reputation_score': profile.reputation_score,
                    'total_reviews': profile.total_reviews,
                    'avg_review_score': float(profile.avg_review_score or Decimal('0.0'))
                }
                cache.set(cache_key, profile_data, self.cache_timeout)
                cached_count += 1
                
            logger.info(f"Warmed {cached_count} user profile cache entries")
            return True
            
        except Exception as e:
            logger.error(f"Failed to warm user profile cache: {str(e)}")
            return False
    
    def _warm_repository_cache(self) -> bool:
        try:
            from apps.repositories.models import Repository
            
            popular_repos = Repository.objects.filter(
                is_public=True,
                star_count__gte=10
            ).order_by('-star_count')[:self.batch_size]
            
            for repo in popular_repos:
                cache_key = f"repository:{repo.id}"
                repo_data = {
                    'name': repo.name,
                    'description': repo.description,
                    'language': repo.primary_language,
                    'star_count': repo.star_count,
                    'fork_count': repo.fork_count
                }
                cache.set(cache_key, repo_data, self.cache_timeout)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to warm repository cache: {str(e)}")
            return False
    
    def _warm_benchmark_metrics_cache(self) -> bool:
        try:
            from apps.benchmarks.models import BenchmarkResult
            
            recent_results = BenchmarkResult.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).select_related('repository', 'user')
            
            metrics_summary = self._calculate_metrics_summary(recent_results)
            cache.set('benchmark_metrics_summary', metrics_summary, self.cache_timeout)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to warm benchmark metrics cache: {str(e)}")
            return False
    
    def _warm_leaderboard_cache(self) -> bool:
        try:
            from apps.users.models import UserProfile
            
            top_users = UserProfile.objects.filter(
                is_active=True
            ).order_by('-reputation_score')[:50]
            
            leaderboard_data = []
            for idx, profile in enumerate(top_users, 1):
                leaderboard_data.append({
                    'rank': idx,
                    'username': profile.user.username,
                    'reputation_score': profile.reputation_score,
                    'total_reviews': profile.total_reviews
                })
            
            cache.set('leaderboard_top_50', leaderboard_data, self.cache_timeout)
            return True
            
        except Exception as e:
            logger.error(f"Failed to warm leaderboard cache: {str(e)}")
            return False
    
    def _calculate_metrics_summary(self, results) -> Dict[str, Any]:
        total_results = results.count()
        if total_results == 0:
            return {'total_results': 0, 'avg_score': 0.0, 'languages': []}
        
        total_score = sum(result.score for result in results)
        avg_score = total_score / total_results
        
        language_counts = {}
        for result in results:
            lang = result.repository.primary_language
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        return {
            'total_results': total_results,
            'avg_score': round(avg_score, 2),
            'languages': list(language_counts.keys())[:10]
        }