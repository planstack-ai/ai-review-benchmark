<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Product;

class ProductListingService
{
    public function getActiveProducts(int $perPage = 20): array
    {
        // BUG: N+1 query problem - category is accessed in loop but not eager loaded
        $products = Product::where('active', true)
            ->orderBy('created_at', 'desc')
            ->paginate($perPage);

        $result = [];
        foreach ($products as $product) {
            // Each iteration triggers a new query to fetch category
            $result[] = [
                'id' => $product->id,
                'name' => $product->name,
                'price' => $product->price,
                'category_name' => $product->category->name, // N+1 here!
                'category_slug' => $product->category->slug,
            ];
        }

        return [
            'products' => $result,
            'pagination' => [
                'total' => $products->total(),
                'per_page' => $products->perPage(),
                'current_page' => $products->currentPage(),
            ],
        ];
    }

    public function getProductsByCategory(int $categoryId, int $perPage = 20): array
    {
        $products = Product::where('category_id', $categoryId)
            ->where('active', true)
            ->orderBy('name')
            ->paginate($perPage);

        $result = [];
        foreach ($products as $product) {
            // Same N+1 issue even though all products are same category
            $result[] = [
                'id' => $product->id,
                'name' => $product->name,
                'price' => $product->price,
                'category_name' => $product->category->name,
            ];
        }

        return [
            'products' => $result,
            'pagination' => [
                'total' => $products->total(),
                'per_page' => $products->perPage(),
                'current_page' => $products->currentPage(),
            ],
        ];
    }
}
