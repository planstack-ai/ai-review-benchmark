<?php

namespace App\Services;

use App\Models\Product;
use App\Models\Category;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\ValidationException;
use Carbon\Carbon;

class ProductBatchService
{
    public function __construct(
        private readonly int $defaultBatchSize = Product::BATCH_SIZE,
        private readonly int $maxBatchSize = Product::MAX_BATCH_SIZE
    ) {}

    public function bulkInsert(array $products, ?int $batchSize = null): array
    {
        $batchSize = $this->validateBatchSize($batchSize);
        $validatedProducts = $this->validateProducts($products);
        $processedProducts = $this->prepareProductsForInsert($validatedProducts);
        
        return $this->insertInBatches($processedProducts, $batchSize);
    }

    public function bulkInsertWithCategories(array $productsData): array
    {
        $categoryMap = $this->ensureCategoriesExist($productsData);
        
        $products = collect($productsData)->map(function ($productData) use ($categoryMap) {
            $productData['category_id'] = $categoryMap[$productData['category_slug']] ?? null;
            unset($productData['category_slug']);
            return $productData;
        })->toArray();

        return $this->bulkInsert($products);
    }

    private function validateBatchSize(?int $batchSize): int
    {
        if ($batchSize === null) {
            return $this->defaultBatchSize;
        }

        return min(max($batchSize, 1), $this->maxBatchSize);
    }

    private function validateProducts(array $products): array
    {
        $validator = Validator::make(['products' => $products], [
            'products' => 'required|array|min:1',
            'products.*.name' => 'required|string|max:255',
            'products.*.sku' => 'required|string|max:255',
            'products.*.price' => 'required|numeric|min:0|max:99999999.99',
            'products.*.stock_quantity' => 'integer|min:0',
            'products.*.category_id' => 'required|integer|exists:categories,id',
            'products.*.is_active' => 'boolean',
        ]);

        if ($validator->fails()) {
            throw new ValidationException($validator);
        }

        return $products;
    }

    private function prepareProductsForInsert(array $products): array
    {
        $now = Carbon::now();
        
        return array_map(function ($product) use ($now) {
            return array_merge([
                'stock_quantity' => 0,
                'is_active' => true,
                'created_at' => $now,
                'updated_at' => $now,
            ], $product);
        }, $products);
    }

    private function insertInBatches(array $products, int $batchSize): array
    {
        $chunks = array_chunk($products, $batchSize);
        $insertedIds = [];
        $totalInserted = 0;

        DB::transaction(function () use ($chunks, &$insertedIds, &$totalInserted) {
            foreach ($chunks as $chunk) {
                $result = DB::table('products')->insert($chunk);
                if ($result) {
                    $totalInserted += count($chunk);
                }
            }
        });

        return [
            'total_processed' => count($products),
            'total_inserted' => $totalInserted,
            'batch_count' => count($chunks),
            'batch_size' => $batchSize,
        ];
    }

    private function ensureCategoriesExist(array $productsData): array
    {
        $categorySlugs = collect($productsData)
            ->pluck('category_slug')
            ->unique()
            ->filter()
            ->values();

        $existingCategories = Category::active()
            ->whereIn('slug', $categorySlugs)
            ->pluck('id', 'slug')
            ->toArray();

        return $existingCategories;
    }
}