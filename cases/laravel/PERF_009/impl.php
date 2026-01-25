<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Category;
use App\Models\Product;
use Illuminate\Support\Facades\Cache;

class CacheService
{
    public function getProductsByCategory(int $categoryId): array
    {
        $cacheKey = "products_category_{$categoryId}";

        // BUG: Cache check then database query is not atomic
        // Multiple concurrent requests can all miss cache and query DB
        if (Cache::has($cacheKey)) {
            return Cache::get($cacheKey);
        }

        // BUG: N+1 query - category accessed for each product
        $products = Product::where('category_id', $categoryId)
            ->where('active', true)
            ->get();

        $result = $products->map(function ($product) {
            return [
                'id' => $product->id,
                'name' => $product->name,
                'price' => $product->price,
                'category' => $product->category->name, // N+1!
            ];
        })->toArray();

        // BUG: No TTL set - cache never expires
        Cache::put($cacheKey, $result);

        return $result;
    }

    public function getAllCategories(): array
    {
        // BUG: Fetches from DB every time, no caching despite method name suggesting it
        return Category::all()->toArray();
    }

    public function clearProductCache(int $productId): void
    {
        $product = Product::find($productId);

        if ($product) {
            // BUG: Only clears this product's category cache
            // Doesn't clear caches that might include this product
            Cache::forget("products_category_{$product->category_id}");
        }
    }

    public function warmCache(): void
    {
        $categories = Category::all();

        // BUG: Sequential cache warming - slow for many categories
        foreach ($categories as $category) {
            // This triggers all the N+1 issues above for each category
            $this->getProductsByCategory($category->id);
        }
    }
}
