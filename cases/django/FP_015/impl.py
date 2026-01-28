from typing import List, Optional, Dict, Any
from django.db import models
from django.db.models import Prefetch, Q
from django.core.exceptions import ValidationError
from decimal import Decimal


class CodeReviewBenchmarkService:
    
    def __init__(self, user_id: int):
        self.user_id = user_id
    
    def get_user_reviews_with_details(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        from .models import CodeReview, ReviewComment, User
        
        queryset = CodeReview.objects.select_related(
            'author',
            'repository',
            'assigned_reviewer'
        ).prefetch_related(
            'comments__author',
            'files__line_comments__author',
            'labels'
        ).filter(author_id=self.user_id)
        
        if status:
            queryset = queryset.filter(status=status)
        
        reviews = queryset.order_by('-created_at')
        return self._format_review_data(reviews)
    
    def get_repository_analytics(self, repository_id: int) -> Dict[str, Any]:
        from .models import CodeReview, Repository
        
        repository = Repository.objects.select_related('owner').get(id=repository_id)
        
        reviews = CodeReview.objects.select_related(
            'author',
            'assigned_reviewer'
        ).prefetch_related(
            'comments',
            'files__line_comments'
        ).filter(repository_id=repository_id)
        
        metrics = self._calculate_repository_metrics(reviews)
        
        return {
            'repository': repository,
            'total_reviews': reviews.count(),
            'metrics': metrics,
            'top_reviewers': self._get_top_reviewers(reviews)
        }
    
    def get_benchmark_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        from .models import User, CodeReview
        
        users = User.objects.prefetch_related(
            Prefetch(
                'authored_reviews',
                queryset=CodeReview.objects.select_related('repository').filter(
                    status='completed'
                )
            ),
            Prefetch(
                'reviewed_reviews',
                queryset=CodeReview.objects.select_related('repository').filter(
                    status='completed'
                )
            )
        ).filter(is_active=True)
        
        leaderboard_data = []
        for user in users:
            score = self._calculate_user_score(user)
            if score > 0:
                leaderboard_data.append({
                    'user': user,
                    'score': score,
                    'reviews_authored': user.authored_reviews.count(),
                    'reviews_completed': user.reviewed_reviews.count()
                })
        
        return sorted(leaderboard_data, key=lambda x: x['score'], reverse=True)[:limit]
    
    def _format_review_data(self, reviews) -> List[Dict[str, Any]]:
        formatted_reviews = []
        for review in reviews:
            comment_count = sum(len(file.line_comments.all()) for file in review.files.all())
            comment_count += review.comments.count()
            
            formatted_reviews.append({
                'id': review.id,
                'title': review.title,
                'author': review.author.username,
                'repository': review.repository.name,
                'status': review.status,
                'comment_count': comment_count,
                'created_at': review.created_at
            })
        
        return formatted_reviews
    
    def _calculate_repository_metrics(self, reviews) -> Dict[str, Decimal]:
        if not reviews.exists():
            return {'avg_review_time': Decimal('0'), 'avg_comments_per_review': Decimal('0')}
        
        total_comments = 0
        completed_reviews = reviews.filter(status='completed')
        
        for review in reviews:
            total_comments += review.comments.count()
            for file in review.files.all():
                total_comments += file.line_comments.count()
        
        avg_comments = Decimal(str(total_comments)) / Decimal(str(reviews.count()))
        
        return {
            'avg_comments_per_review': avg_comments.quantize(Decimal('0.01')),
            'completion_rate': self._calculate_completion_rate(reviews, completed_reviews)
        }
    
    def _get_top_reviewers(self, reviews) -> List[Dict[str, Any]]:
        reviewer_stats = {}
        
        for review in reviews:
            if review.assigned_reviewer:
                reviewer_id = review.assigned_reviewer.id
                if reviewer_id not in reviewer_stats:
                    reviewer_stats[reviewer_id] = {
                        'user': review.assigned_reviewer,
                        'review_count': 0
                    }
                reviewer_stats[reviewer_id]['review_count'] += 1
        
        return sorted(reviewer_stats.values(), key=lambda x: x['review_count'], reverse=True)[:5]
    
    def _calculate_user_score(self, user) -> Decimal:
        authored_weight = Decimal('1.0')
        reviewed_weight = Decimal('1.5')
        
        authored_score = Decimal(str(user.authored_reviews.count())) * authored_weight
        reviewed_score = Decimal(str(user.reviewed_reviews.count())) * reviewed_weight
        
        return authored_score + reviewed_score
    
    def _calculate_completion_rate(self, all_reviews, completed_reviews) -> Decimal:
        if not all_reviews.exists():
            return Decimal('0')
        
        rate = Decimal(str(completed_reviews.count())) / Decimal(str(all_reviews.count()))
        return (rate * Decimal('100')).quantize(Decimal('0.01'))