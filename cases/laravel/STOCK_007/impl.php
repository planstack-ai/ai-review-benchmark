<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\StockTransfer;
use App\Models\WarehouseStock;
use Illuminate\Support\Facades\DB;

class StockTransferService
{
    public function initiateTransfer(
        int $productId,
        int $sourceWarehouseId,
        int $destinationWarehouseId,
        int $quantity
    ): array {
        if ($sourceWarehouseId === $destinationWarehouseId) {
            return [
                'success' => false,
                'message' => 'Source and destination must be different',
            ];
        }

        $sourceStock = WarehouseStock::where('warehouse_id', $sourceWarehouseId)
            ->where('product_id', $productId)
            ->first();

        if (!$sourceStock) {
            return [
                'success' => false,
                'message' => 'Product not found in source warehouse',
            ];
        }

        // BUG: Checks total quantity instead of available quantity
        // Should use availableQuantity() to exclude reserved stock
        if ($sourceStock->quantity < $quantity) {
            return [
                'success' => false,
                'message' => 'Insufficient stock in source warehouse',
            ];
        }

        return DB::transaction(function () use ($productId, $sourceWarehouseId, $destinationWarehouseId, $quantity, $sourceStock) {
            $transfer = StockTransfer::create([
                'product_id' => $productId,
                'source_warehouse_id' => $sourceWarehouseId,
                'destination_warehouse_id' => $destinationWarehouseId,
                'quantity' => $quantity,
                'status' => 'pending',
            ]);

            return [
                'success' => true,
                'transfer' => $transfer,
            ];
        });
    }

    public function shipTransfer(int $transferId): array
    {
        return DB::transaction(function () use ($transferId) {
            $transfer = StockTransfer::lockForUpdate()->findOrFail($transferId);

            if ($transfer->status !== 'pending') {
                return [
                    'success' => false,
                    'message' => 'Transfer is not pending',
                ];
            }

            // Deduct from source warehouse
            WarehouseStock::where('warehouse_id', $transfer->source_warehouse_id)
                ->where('product_id', $transfer->product_id)
                ->decrement('quantity', $transfer->quantity);

            $transfer->update([
                'status' => 'in_transit',
                'shipped_at' => now(),
            ]);

            return [
                'success' => true,
                'transfer' => $transfer,
            ];
        });
    }

    public function confirmReceipt(int $transferId): array
    {
        return DB::transaction(function () use ($transferId) {
            $transfer = StockTransfer::lockForUpdate()->findOrFail($transferId);

            if ($transfer->status !== 'in_transit') {
                return [
                    'success' => false,
                    'message' => 'Transfer is not in transit',
                ];
            }

            // Add to destination warehouse
            $destStock = WarehouseStock::firstOrCreate(
                [
                    'warehouse_id' => $transfer->destination_warehouse_id,
                    'product_id' => $transfer->product_id,
                ],
                [
                    'quantity' => 0,
                    'reserved_quantity' => 0,
                ]
            );

            $destStock->increment('quantity', $transfer->quantity);

            $transfer->update([
                'status' => 'completed',
                'received_at' => now(),
            ]);

            return [
                'success' => true,
                'transfer' => $transfer,
            ];
        });
    }

    public function cancelTransfer(int $transferId): array
    {
        return DB::transaction(function () use ($transferId) {
            $transfer = StockTransfer::lockForUpdate()->findOrFail($transferId);

            if ($transfer->status === 'completed') {
                return [
                    'success' => false,
                    'message' => 'Completed transfers cannot be cancelled',
                ];
            }

            if ($transfer->status === 'in_transit') {
                // Return stock to source
                WarehouseStock::where('warehouse_id', $transfer->source_warehouse_id)
                    ->where('product_id', $transfer->product_id)
                    ->increment('quantity', $transfer->quantity);
            }

            $transfer->update(['status' => 'cancelled']);

            return [
                'success' => true,
            ];
        });
    }
}
