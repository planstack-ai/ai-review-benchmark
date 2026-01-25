<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\InventoryLog;
use App\Models\Product;
use Illuminate\Support\Facades\DB;

class InventoryManagementService
{
    public function adjustStock(int $productId, int $quantityChange, string $reason): array
    {
        return DB::transaction(function () use ($productId, $quantityChange, $reason) {
            // Lock the product row to prevent concurrent modifications
            $product = Product::lockForUpdate()->findOrFail($productId);

            $stockBefore = $product->stock_quantity;
            $stockAfter = $stockBefore + $quantityChange;

            // Prevent negative stock
            if ($stockAfter < 0) {
                return [
                    'success' => false,
                    'message' => 'Insufficient stock for this adjustment',
                ];
            }

            // Update stock
            $product->stock_quantity = $stockAfter;
            $product->save();

            // Log the change
            InventoryLog::create([
                'product_id' => $productId,
                'quantity_change' => $quantityChange,
                'stock_before' => $stockBefore,
                'stock_after' => $stockAfter,
                'reason' => $reason,
            ]);

            return [
                'success' => true,
                'stock_before' => $stockBefore,
                'stock_after' => $stockAfter,
            ];
        });
    }

    public function reserveStock(int $productId, int $quantity): array
    {
        if ($quantity <= 0) {
            return [
                'success' => false,
                'message' => 'Quantity must be positive',
            ];
        }

        return $this->adjustStock($productId, -$quantity, 'Stock reserved for order');
    }

    public function releaseStock(int $productId, int $quantity): array
    {
        if ($quantity <= 0) {
            return [
                'success' => false,
                'message' => 'Quantity must be positive',
            ];
        }

        return $this->adjustStock($productId, $quantity, 'Stock released from cancelled order');
    }

    public function getStockHistory(int $productId, int $limit = 50): array
    {
        $logs = InventoryLog::where('product_id', $productId)
            ->orderBy('created_at', 'desc')
            ->limit($limit)
            ->get();

        return $logs->toArray();
    }
}
