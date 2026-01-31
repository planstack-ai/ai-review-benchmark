<?php

namespace App\Services;

use App\Models\Category;
use App\Models\Post;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Facades\DB;

class CounterCacheService
{
    public function __construct(
        private readonly Category $categoryModel,
        private readonly Post $postModel
    ) {}

    public function updateCategoryPostsCount(int $categoryId): void
    {
        $count = $this->postModel
            ->where('category_id', $categoryId)
            ->published()
            ->count();

        $this->categoryModel
            ->where('id', $categoryId)
            ->update(['posts_count' => $count]);
    }

    public function incrementCategoryPostsCount(int $categoryId, int $increment = 1): void
    {
        $this->categoryModel
            ->where('id', $categoryId)
            ->increment('posts_count', $increment);
    }

    public function decrementCategoryPostsCount(int $categoryId, int $decrement = 1): void
    {
        $this->categoryModel
            ->where('id', $categoryId)
            ->where('posts_count', '>=', $decrement)
            ->decrement('posts_count', $decrement);
    }

    public function recalculateAllCategoryCounts(): void
    {
        $categories = $this->categoryModel->all();

        foreach ($categories as $category) {
            $this->updateCategoryPostsCount($category->id);
        }
    }

    public function batchUpdateCategoryCounts(array $categoryIds): void
    {
        $counts = $this->postModel
            ->select('category_id', DB::raw('COUNT(*) as posts_count'))
            ->whereIn('category_id', $categoryIds)
            ->published()
            ->groupBy('category_id')
            ->pluck('posts_count', 'category_id')
            ->toArray();

        foreach ($categoryIds as $categoryId) {
            $count = $counts[$categoryId] ?? 0;
            $this->categoryModel
                ->where('id', $categoryId)
                ->update(['posts_count' => $count]);
        }
    }

    public function handlePostStatusChange(Post $post, string $oldStatus): void
    {
        $wasPublished = $oldStatus === Post::STATUS_PUBLISHED;
        $isPublished = $post->status === Post::STATUS_PUBLISHED;

        if (!$wasPublished && $isPublished) {
            $this->incrementCategoryPostsCount($post->category_id);
        } elseif ($wasPublished && !$isPublished) {
            $this->decrementCategoryPostsCount($post->category_id);
        }
    }

    public function getCategoriesWithAccurateCounts(): Collection
    {
        return $this->categoryModel
            ->active()
            ->withCount('publishedPosts')
            ->get()
            ->map(function ($category) {
                if ($category->posts_count !== $category->published_posts_count) {
                    $this->updateCategoryPostsCount($category->id);
                    $category->refresh();
                }
                return $category;
            });
    }

    private function validateCategoryExists(int $categoryId): bool
    {
        return $this->categoryModel->where('id', $categoryId)->exists();
    }
}