<?php

namespace App\Services;

use App\Models\Product;
use App\Models\Category;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Collection;
use Carbon\Carbon;

class ProductBulkUpdateService
{
    public function __construct(
        private readonly int $batchSize = 500
    ) {}

    public function bulkUpdatePrices(array $priceUpdates): int
    {
        $updatedCount = 0;
        $chunks = array_chunk($priceUpdates, $this->batchSize);

        DB::transaction(function () use ($chunks, &$updatedCount) {
            foreach ($chunks as $chunk) {
                $updatedCount += $this->processPriceChunk($chunk);
            }
        });

        return $updatedCount;
    }

    public function bulkUpdateStock(array $stockUpdates, bool $updateRestockDate = true): int
    {
        $updatedCount = 0;
        $chunks = array_chunk($stockUpdates, $this->batchSize);

        DB::transaction(function () use ($chunks, $updateRestockDate, &$updatedCount) {
            foreach ($chunks as $chunk) {
                $updatedCount += $this->processStockChunk($chunk, $updateRestockDate);
            }
        });

        return $updatedCount;
    }

    public function bulkActivateByCategory(int $categoryId): int
    {
        return DB::table('products')
            ->where('category_id', $categoryId)
            ->update([
                'is_active' => true,
                'updated_at' => now()
            ]);
    }

    public function bulkDeactivateOutOfStock(): int
    {
        return DB::table('products')
            ->where('stock_quantity', '<=', Product::OUT_OF_STOCK_THRESHOLD)
            ->update([
                'is_active' => false,
                'updated_at' => now()
            ]);
    }

    public function bulkUpdateCategoryProducts(int $categoryId, array $updates): int
    {
        $allowedFields = ['price', 'is_active', 'stock_quantity'];
        $filteredUpdates = array_intersect_key($updates, array_flip($allowedFields));
        
        if (empty($filteredUpdates)) {
            return 0;
        }

        $filteredUpdates['updated_at'] = now();

        return DB::table('products')
            ->where('category_id', $categoryId)
            ->update($filteredUpdates);
    }

    private function processPriceChunk(array $chunk): int
    {
        $cases = [];
        $ids = [];

        foreach ($chunk as $update) {
            $productId = (int) $update['id'];
            $price = (float) $update['price'];
            
            $cases[] = "WHEN {$productId} THEN {$price}";
            $ids[] = $productId;
        }

        if (empty($cases)) {
            return 0;
        }

        $caseSql = implode(' ', $cases);
        $idsString = implode(',', $ids);

        return DB::update("
            UPDATE products 
            SET price = CASE id {$caseSql} END,
                updated_at = ?
            WHERE id IN ({$idsString})
        ", [now()]);
    }

    private function processStockChunk(array $chunk, bool $updateRestockDate): int
    {
        $stockCases = [];
        $restockCases = [];
        $ids = [];

        foreach ($chunk as $update) {
            $productId = (int) $update['id'];
            $quantity = (int) $update['quantity'];
            
            $stockCases[] = "WHEN {$productId} THEN {$quantity}";
            $ids[] = $productId;

            if ($updateRestockDate && $quantity > 0) {
                $restockCases[] = "WHEN {$productId} THEN '" . now()->toDateTimeString() . "'";
            }
        }

        if (empty($stockCases)) {
            return 0;
        }

        $stockCaseSql = implode(' ', $stockCases);
        $idsString = implode(',', $ids);

        $sql = "UPDATE products SET stock_quantity = CASE id {$stockCaseSql} END";

        if (!empty($restockCases)) {
            $restockCaseSql = implode(' ', $restockCases);
            $sql .= ", last_restocked_at = CASE id {$restockCaseSql} ELSE last_restocked_at END";
        }

        $sql .= ", updated_at = ? WHERE id IN ({$idsString})";

        return DB::update($sql, [now()]);
    }
}