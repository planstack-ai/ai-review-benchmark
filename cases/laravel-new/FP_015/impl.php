<?php

namespace App\Services;

use App\Models\Post;
use App\Models\User;
use App\Models\Comment;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Pagination\LengthAwarePaginator;

class PostAnalyticsService
{
    public function __construct(
        private readonly int $defaultPerPage = 15
    ) {}

    public function getTopAuthorsWithEngagement(int $limit = 10): Collection
    {
        return User::active()
            ->with(['posts' => function ($query) {
                $query->published()->with('comments');
            }])
            ->whereHas('posts', function ($query) {
                $query->published();
            })
            ->get()
            ->map(function (User $user) {
                $totalPosts = $user->posts->count();
                $totalComments = $user->posts->sum(fn($post) => $post->comments->count());
                
                return [
                    'user' => $user,
                    'posts_count' => $totalPosts,
                    'comments_count' => $totalComments,
                    'engagement_score' => $this->calculateEngagementScore($totalPosts, $totalComments)
                ];
            })
            ->sortByDesc('engagement_score')
            ->take($limit)
            ->values();
    }

    public function getPostsWithFullContext(array $filters = []): LengthAwarePaginator
    {
        $query = Post::withAuthorAndComments()
            ->published();

        if (isset($filters['author_id'])) {
            $query->where('user_id', $filters['author_id']);
        }

        if (isset($filters['has_comments']) && $filters['has_comments']) {
            $query->whereHas('comments');
        }

        return $query->paginate($this->defaultPerPage);
    }

    public function generateUserActivityReport(int $userId): array
    {
        $user = User::with([
            'posts.comments.user',
            'comments.post.user'
        ])->findOrFail($userId);

        $publishedPosts = $user->posts->where('status', Post::STATUS_PUBLISHED);
        $userComments = $user->comments->where('is_approved', true);

        return [
            'user' => $user,
            'published_posts' => $publishedPosts,
            'total_comments_received' => $this->countCommentsOnUserPosts($publishedPosts),
            'comments_made' => $userComments,
            'activity_score' => $this->calculateActivityScore($publishedPosts->count(), $userComments->count())
        ];
    }

    public function getMostCommentedPosts(int $limit = 20): Collection
    {
        return Post::published()
            ->with(['user', 'approvedComments.user'])
            ->get()
            ->map(function (Post $post) {
                return [
                    'post' => $post,
                    'approved_comments_count' => $post->approvedComments->count(),
                    'total_comments_count' => $post->comments->count()
                ];
            })
            ->sortByDesc('approved_comments_count')
            ->take($limit)
            ->values();
    }

    private function calculateEngagementScore(int $postsCount, int $commentsCount): float
    {
        if ($postsCount === 0) {
            return 0.0;
        }

        $avgCommentsPerPost = $commentsCount / $postsCount;
        return round($avgCommentsPerPost * 10 + $postsCount * 0.5, 2);
    }

    private function calculateActivityScore(int $postsCount, int $commentsCount): int
    {
        return ($postsCount * 5) + ($commentsCount * 2);
    }

    private function countCommentsOnUserPosts(Collection $posts): int
    {
        return $posts->sum(function (Post $post) {
            return $post->comments->where('is_approved', true)->count();
        });
    }
}