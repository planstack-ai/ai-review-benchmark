<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\PriceHistory;
use App\Models\Product;
use Illuminate\Support\Facades\DB;

class BatchUpdateService
{
    public function updatePrices(array $priceUpdates): array
    {
        // $priceUpdates = [['product_id' => 1, 'new_price' => 99.99], ...]

        $updated = 0;
        $failed = 0;

        foreach ($priceUpdates as $update) {
            try {
                // BUG: Individual SELECT for each product
                $product = Product::find($update['product_id']);

                if (!$product) {
                    $failed++;
                    continue;
                }

                $oldPrice = $product->price;

                // BUG: Individual UPDATE for each product
                $product->update(['price' => $update['new_price']]);

                // BUG: Individual INSERT for each history record
                PriceHistory::create([
                    'product_id' => $product->id,
                    'old_price' => $oldPrice,
                    'new_price' => $update['new_price'],
                ]);

                $updated++;
            } catch (\Exception $e) {
                $failed++;
            }
        }

        return [
            'updated' => $updated,
            'failed' => $failed,
        ];
    }

    public function deactivateProducts(array $productIds): int
    {
        $deactivated = 0;

        // BUG: Individual UPDATE for each product
        foreach ($productIds as $id) {
            $product = Product::find($id);
            if ($product && $product->active) {
                $product->update(['active' => false]);
                $deactivated++;
            }
        }

        return $deactivated;
    }

    public function bulkPriceIncrease(float $percentage): int
    {
        // BUG: Loads all products, updates one by one
        $products = Product::where('active', true)->get();

        $updated = 0;
        foreach ($products as $product) {
            $newPrice = $product->price * (1 + $percentage / 100);
            $product->update(['price' => round($newPrice, 2)]);
            $updated++;
        }

        return $updated;
    }
}
