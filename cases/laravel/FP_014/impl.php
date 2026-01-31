<?php

namespace App\Services;

use App\Models\Post;
use App\Models\Category;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Pagination\LengthAwarePaginator;
use Carbon\Carbon;

class PostAnalyticsService
{
    public function __construct(
        private readonly int $defaultPageSize = 15
    ) {}

    public function getPostsByStatus(string $status, int $page = 1): LengthAwarePaginator
    {
        return Post::byStatus($status)
            ->with(['user', 'categories'])
            ->orderBy('created_at', 'desc')
            ->paginate($this->defaultPageSize, ['*'], 'page', $page);
    }

    public function getFeaturedPostsAnalytics(): array
    {
        $featuredPosts = Post::featured()
            ->published()
            ->with('categories')
            ->get();

        return [
            'total_featured' => $featuredPosts->count(),
            'published_featured' => $featuredPosts->where('is_published', true)->count(),
            'categories_distribution' => $this->getCategoryDistribution($featuredPosts),
            'monthly_breakdown' => $this->getMonthlyBreakdown($featuredPosts),
        ];
    }

    public function getRecentPostsReport(int $days = 30): Collection
    {
        return Post::recent($days)
            ->with(['user', 'categories'])
            ->where('status', 'published')
            ->orderBy('published_at', 'desc')
            ->get();
    }

    public function getCategoryPerformance(): array
    {
        $categories = Category::active()
            ->with(['posts' => function ($query) {
                $query->published();
            }])
            ->get();

        return $categories->map(function ($category) {
            return [
                'id' => $category->id,
                'name' => $category->name,
                'slug' => $category->slug,
                'post_count' => $category->post_count,
                'recent_posts' => $category->posts()
                    ->published()
                    ->recent(7)
                    ->count(),
            ];
        })->toArray();
    }

    public function getStatusDistribution(): array
    {
        $statusCounts = [];
        $statuses = ['draft', 'published', 'archived'];

        foreach ($statuses as $status) {
            $statusCounts[$status] = Post::byStatus($status)->count();
        }

        return $statusCounts;
    }

    private function getCategoryDistribution(Collection $posts): array
    {
        $distribution = [];
        
        foreach ($posts as $post) {
            foreach ($post->categories as $category) {
                $distribution[$category->name] = ($distribution[$category->name] ?? 0) + 1;
            }
        }

        return $distribution;
    }

    private function getMonthlyBreakdown(Collection $posts): array
    {
        return $posts->groupBy(function ($post) {
            return $post->published_at?->format('Y-m') ?? 'unpublished';
        })->map(function ($monthPosts) {
            return $monthPosts->count();
        })->toArray();
    }

    private function calculateEngagementScore(Post $post): float
    {
        $baseScore = $post->is_featured ? 10.0 : 5.0;
        $categoryMultiplier = $post->categories->count() * 0.5;
        $ageMultiplier = $this->getAgeMultiplier($post->published_at);

        return round($baseScore + $categoryMultiplier + $ageMultiplier, 2);
    }

    private function getAgeMultiplier(?Carbon $publishedAt): float
    {
        if (!$publishedAt) {
            return 0.0;
        }

        $daysOld = $publishedAt->diffInDays(now());
        
        return max(0, 5.0 - ($daysOld * 0.1));
    }
}