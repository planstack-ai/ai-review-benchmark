<?php

namespace App\Services;

use App\Models\Product;
use App\Models\Category;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Cache;

class ProductCatalogService
{
    private const CACHE_TTL = 3600;
    private const CACHE_PREFIX = 'product_catalog';

    public function __construct(
        private readonly Product $productModel,
        private readonly Category $categoryModel
    ) {}

    public function getFeaturedProducts(int $limit = 12): Collection
    {
        $cacheKey = $this->getCacheKey('featured', $limit);

        return Cache::remember($cacheKey, self::CACHE_TTL, function () use ($limit) {
            return $this->productModel
                ->active()
                ->inStock()
                ->with(['category:id,name,slug', 'approvedReviews:id,product_id,rating'])
                ->withCount('approvedReviews')
                ->withAvg('approvedReviews', 'rating')
                ->orderByDesc('approved_reviews_avg_rating')
                ->orderByDesc('approved_reviews_count')
                ->limit($limit)
                ->get()
                ->map(function ($product) {
                    return $this->enrichProductData($product);
                });
        });
    }

    public function getProductsByCategory(int $categoryId, array $filters = []): Collection
    {
        $cacheKey = $this->getCacheKey('category', $categoryId, serialize($filters));

        return Cache::remember($cacheKey, self::CACHE_TTL, function () use ($categoryId, $filters) {
            $query = $this->productModel
                ->active()
                ->where('category_id', $categoryId)
                ->with(['category:id,name,slug', 'approvedReviews:id,product_id,rating'])
                ->withCount('approvedReviews')
                ->withAvg('approvedReviews', 'rating');

            if (isset($filters['in_stock']) && $filters['in_stock']) {
                $query->inStock();
            }

            if (isset($filters['min_price'], $filters['max_price'])) {
                $query->byPriceRange($filters['min_price'], $filters['max_price']);
            }

            $sortBy = $filters['sort_by'] ?? 'name';
            $sortDirection = $filters['sort_direction'] ?? 'asc';

            return $query
                ->orderBy($sortBy, $sortDirection)
                ->get()
                ->map(function ($product) {
                    return $this->enrichProductData($product);
                });
        });
    }

    public function getCategoriesWithProductCounts(): Collection
    {
        $cacheKey = $this->getCacheKey('categories_with_counts');

        return Cache::remember($cacheKey, self::CACHE_TTL, function () {
            return $this->categoryModel
                ->active()
                ->withCount(['products' => function ($query) {
                    $query->active();
                }])
                ->having('products_count', '>', 0)
                ->orderBy('name')
                ->get();
        });
    }

    public function getTopRatedProducts(int $limit = 10): Collection
    {
        $cacheKey = $this->getCacheKey('top_rated', $limit);

        return Cache::remember($cacheKey, self::CACHE_TTL, function () use ($limit) {
            return $this->productModel
                ->active()
                ->inStock()
                ->with(['category:id,name,slug', 'approvedReviews:id,product_id,rating'])
                ->withCount('approvedReviews')
                ->withAvg('approvedReviews', 'rating')
                ->having('approved_reviews_count', '>=', 5)
                ->orderByDesc('approved_reviews_avg_rating')
                ->orderByDesc('approved_reviews_count')
                ->limit($limit)
                ->get()
                ->map(function ($product) {
                    return $this->enrichProductData($product);
                });
        });
    }

    public function clearCache(): void
    {
        $tags = [self::CACHE_PREFIX];
        Cache::tags($tags)->flush();
    }

    private function enrichProductData(Product $product): Product
    {
        $product->average_rating = round($product->approved_reviews_avg_rating ?? 0, 1);
        $product->review_count = $product->approved_reviews_count ?? 0;
        $product->is_in_stock = $product->stock_quantity > 0;
        $product->category_name = $product->category?->name;

        return $product;
    }

    private function getCacheKey(string ...$parts): string
    {
        return self::CACHE_PREFIX . ':' . implode(':', $parts);
    }
}