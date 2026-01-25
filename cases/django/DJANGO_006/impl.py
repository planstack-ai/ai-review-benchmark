from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import transaction
from typing import Optional, Dict, Any
from .models import CodeReview, ReviewComment, Project
from .forms import CodeReviewForm, CommentForm


class CodeReviewService:
    """Service class for managing AI code review benchmarks and user interactions."""
    
    def __init__(self):
        self.max_comments_per_review = 50
        self.allowed_file_extensions = ['.py', '.js', '.java', '.cpp', '.c']
    
    @login_required
    def create_review(self, request):
        """Create a new code review with proper authentication."""
        if request.method == 'POST':
            form = CodeReviewForm(request.POST, request.FILES)
            if form.is_valid():
                review = form.save(commit=False)
                review.author = request.user
                review.save()
                messages.success(request, 'Code review created successfully!')
                return redirect('review_detail', review_id=review.id)
        else:
            form = CodeReviewForm()
        
        return render(request, 'reviews/create_review.html', {'form': form})
    
    def view_review_details(self, request, review_id: int):
        """Display detailed view of a specific code review."""
        review = get_object_or_404(CodeReview, id=review_id)
        comments = self._get_review_comments(review)
        
        context = {
            'review': review,
            'comments': comments,
            'can_edit': self._can_user_edit_review(request.user, review),
            'comment_form': CommentForm() if request.user.is_authenticated else None
        }
        
        return render(request, 'reviews/review_detail.html', context)
    
    @login_required
    def add_comment(self, request, review_id: int):
        """Add a comment to an existing code review."""
        review = get_object_or_404(CodeReview, id=review_id)
        
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                if self._validate_comment_limit(review):
                    comment = form.save(commit=False)
                    comment.review = review
                    comment.author = request.user
                    comment.save()
                    return JsonResponse({'status': 'success', 'comment_id': comment.id})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Comment limit exceeded'})
        
        return JsonResponse({'status': 'error', 'message': 'Invalid form data'})
    
    def list_user_reviews(self, request):
        """List all code reviews created by the current user."""
        user_reviews = CodeReview.objects.filter(author=request.user).order_by('-created_at')
        
        paginated_reviews = self._paginate_reviews(request, user_reviews)
        
        context = {
            'reviews': paginated_reviews,
            'total_count': user_reviews.count(),
            'user_stats': self._calculate_user_stats(request.user)
        }
        
        return render(request, 'reviews/user_reviews.html', context)
    
    @login_required
    @require_http_methods(["DELETE"])
    def delete_review(self, request, review_id: int):
        """Delete a code review if user has permission."""
        review = get_object_or_404(CodeReview, id=review_id)
        
        if not self._can_user_edit_review(request.user, review):
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        
        try:
            with transaction.atomic():
                review.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    def _get_review_comments(self, review: CodeReview) -> list:
        """Retrieve all comments for a given review."""
        return review.comments.select_related('author').order_by('created_at')
    
    def _can_user_edit_review(self, user, review: CodeReview) -> bool:
        """Check if user has permission to edit the review."""
        return user.is_authenticated and (user == review.author or user.is_staff)
    
    def _validate_comment_limit(self, review: CodeReview) -> bool:
        """Validate that the review hasn't exceeded the comment limit."""
        current_count = review.comments.count()
        return current_count < self.max_comments_per_review
    
    def _paginate_reviews(self, request, queryset):
        """Apply pagination to review queryset."""
        from django.core.paginator import Paginator
        
        paginator = Paginator(queryset, 10)
        page_number = request.GET.get('page', 1)
        return paginator.get_page(page_number)
    
    def _calculate_user_stats(self, user) -> Dict[str, Any]:
        """Calculate statistics for the user's reviews."""
        reviews = CodeReview.objects.filter(author=user)
        return {
            'total_reviews': reviews.count(),
            'total_comments': ReviewComment.objects.filter(review__author=user).count(),
            'avg_rating': reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating'] or 0
        }