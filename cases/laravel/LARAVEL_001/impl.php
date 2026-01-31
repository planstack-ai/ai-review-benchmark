<?php

namespace App\Services;

use App\Models\Product;
use App\Models\Category;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Facades\Cache;

class ProductCatalogService
{
    public function __construct(
        private readonly Product $productModel,
        private readonly Category $categoryModel
    ) {}

    public function getFeaturedProducts(int $limit = 12): Collection
    {
        return $this->productModel
            ->where('is_active', true)
            ->whereNull('deleted_at')
            ->where('is_featured', true)
            ->orderBy('featured_order')
            ->limit($limit)
            ->get();
    }

    public function getProductsByCategory(int $categoryId, int $perPage = 20): LengthAwarePaginator
    {
        return $this->productModel
            ->where('is_active', true)
            ->whereNull('deleted_at')
            ->where('category_id', $categoryId)
            ->orderBy('name')
            ->paginate($perPage);
    }

    public function searchProducts(string $query, array $filters = []): Collection
    {
        $products = $this->productModel
            ->where('is_active', true)
            ->whereNull('deleted_at')
            ->where(function ($q) use ($query) {
                $q->where('name', 'like', "%{$query}%")
                  ->orWhere('description', 'like', "%{$query}%")
                  ->orWhere('sku', 'like', "%{$query}%");
            });

        if (isset($filters['price_min'])) {
            $products->where('price', '>=', $filters['price_min']);
        }

        if (isset($filters['price_max'])) {
            $products->where('price', '<=', $filters['price_max']);
        }

        if (isset($filters['brand_id'])) {
            $products->where('brand_id', $filters['brand_id']);
        }

        return $products->orderBy('name')->get();
    }

    public function getNewArrivals(int $days = 30, int $limit = 24): Collection
    {
        $cutoffDate = now()->subDays($days);

        return $this->productModel
            ->where('is_active', true)
            ->whereNull('deleted_at')
            ->where('created_at', '>=', $cutoffDate)
            ->orderBy('created_at', 'desc')
            ->limit($limit)
            ->get();
    }

    public function getDiscountedProducts(float $minDiscountPercent = 10): Collection
    {
        return $this->productModel
            ->where('is_active', true)
            ->whereNull('deleted_at')
            ->whereNotNull('sale_price')
            ->whereRaw('((price - sale_price) / price * 100) >= ?', [$minDiscountPercent])
            ->orderBy('created_at', 'desc')
            ->get();
    }

    public function getCachedCategoryProducts(int $categoryId): Collection
    {
        $cacheKey = "category_products_{$categoryId}";

        return Cache::remember($cacheKey, 3600, function () use ($categoryId) {
            return $this->getActiveProductsForCategory($categoryId);
        });
    }

    private function getActiveProductsForCategory(int $categoryId): Collection
    {
        return $this->productModel
            ->where('is_active', true)
            ->whereNull('deleted_at')
            ->where('category_id', $categoryId)
            ->with(['category', 'brand'])
            ->orderBy('sort_order')
            ->orderBy('name')
            ->get();
    }

    public function getProductRecommendations(int $productId, int $limit = 6): Collection
    {
        $product = $this->productModel->find($productId);
        
        if (!$product) {
            return new Collection();
        }

        return $this->productModel
            ->where('is_active', true)
            ->whereNull('deleted_at')
            ->where('category_id', $product->category_id)
            ->where('id', '!=', $productId)
            ->inRandomOrder()
            ->limit($limit)
            ->get();
    }
}