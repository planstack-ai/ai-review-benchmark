<?php

namespace App\Services;

use App\Models\Product;
use App\Models\Category;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;

class ProductCatalogService
{
    public function __construct(
        private readonly int $cacheTimeout = 3600,
        private readonly int $defaultPerPage = 20
    ) {}

    public function getFeaturedProducts(int $limit = 10): Collection
    {
        return Cache::remember('featured_products', $this->cacheTimeout, function () use ($limit) {
            return Product::where('is_featured', true)
                ->where('is_active', true)
                ->orderBy('featured_order')
                ->limit($limit)
                ->get();
        });
    }

    public function searchProducts(
        string $query,
        ?int $categoryId = null,
        array $filters = [],
        int $page = 1
    ): LengthAwarePaginator {
        $baseQuery = $this->buildSearchQuery($query, $categoryId, $filters);
        
        return $baseQuery->paginate(
            $this->defaultPerPage,
            ['*'],
            'page',
            $page
        );
    }

    public function getProductsByCategory(int $categoryId, array $sortOptions = []): Collection
    {
        $cacheKey = "category_products_{$categoryId}_" . md5(serialize($sortOptions));
        
        return Cache::remember($cacheKey, $this->cacheTimeout, function () use ($categoryId, $sortOptions) {
            $query = Product::where('category_id', $categoryId)
                ->where('is_active', true);

            $this->applySorting($query, $sortOptions);

            return $query->get();
        });
    }

    public function getRelatedProducts(Product $product, int $limit = 6): Collection
    {
        return Product::where('category_id', $product->category_id)
            ->where('id', '!=', $product->id)
            ->where('is_active', true)
            ->inRandomOrder()
            ->limit($limit)
            ->get();
    }

    public function getProductsOnSale(int $limit = 20): Collection
    {
        return Product::whereNotNull('sale_price')
            ->where('sale_price', '>', 0)
            ->where('is_active', true)
            ->orderBy('discount_percentage', 'desc')
            ->limit($limit)
            ->get();
    }

    private function buildSearchQuery(string $query, ?int $categoryId, array $filters)
    {
        $searchQuery = Product::where('is_active', true)
            ->where(function ($q) use ($query) {
                $q->where('name', 'LIKE', "%{$query}%")
                  ->orWhere('description', 'LIKE', "%{$query}%")
                  ->orWhere('sku', 'LIKE', "%{$query}%");
            });

        if ($categoryId) {
            $searchQuery->where('category_id', $categoryId);
        }

        $this->applyFilters($searchQuery, $filters);

        return $searchQuery->orderBy('relevance_score', 'desc');
    }

    private function applyFilters($query, array $filters): void
    {
        if (isset($filters['price_min'])) {
            $query->where('price', '>=', $filters['price_min']);
        }

        if (isset($filters['price_max'])) {
            $query->where('price', '<=', $filters['price_max']);
        }

        if (isset($filters['brand_ids']) && is_array($filters['brand_ids'])) {
            $query->whereIn('brand_id', $filters['brand_ids']);
        }

        if (isset($filters['in_stock']) && $filters['in_stock']) {
            $query->where('stock_quantity', '>', 0);
        }
    }

    private function applySorting($query, array $sortOptions): void
    {
        $sortBy = $sortOptions['sort_by'] ?? 'name';
        $sortDirection = $sortOptions['direction'] ?? 'asc';

        match ($sortBy) {
            'price' => $query->orderBy('price', $sortDirection),
            'created_at' => $query->orderBy('created_at', $sortDirection),
            'popularity' => $query->orderBy('view_count', $sortDirection),
            default => $query->orderBy('name', $sortDirection)
        };
    }

    public function clearCatalogCache(): void
    {
        Cache::forget('featured_products');
        
        $categoryIds = Category::pluck('id');
        foreach ($categoryIds as $categoryId) {
            Cache::tags(['category_products'])->flush();
        }
    }
}