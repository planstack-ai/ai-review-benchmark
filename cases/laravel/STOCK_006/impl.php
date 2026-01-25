<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Order;
use App\Models\Preorder;
use App\Models\Product;
use App\Notifications\PreorderReadyNotification;
use Illuminate\Support\Facades\DB;

class PreorderService
{
    public function createPreorder(int $userId, int $productId, int $quantity): array
    {
        $product = Product::findOrFail($productId);

        if (!$product->preorder_enabled) {
            return [
                'success' => false,
                'message' => 'Preorders not available for this product',
            ];
        }

        // BUG: Uses expected_quantity directly instead of available preorder slots
        // Should be: expected_quantity - preorder_count
        $availableSlots = $product->expected_quantity;

        if ($quantity > $availableSlots) {
            return [
                'success' => false,
                'message' => 'Requested quantity exceeds available preorder slots',
            ];
        }

        return DB::transaction(function () use ($userId, $productId, $quantity, $product) {
            $preorder = Preorder::create([
                'user_id' => $userId,
                'product_id' => $productId,
                'quantity' => $quantity,
                'status' => 'pending',
            ]);

            $product->increment('preorder_count', $quantity);

            return [
                'success' => true,
                'preorder' => $preorder,
                'expected_arrival' => $product->expected_arrival_date,
            ];
        });
    }

    public function processStockArrival(int $productId, int $arrivedQuantity): array
    {
        return DB::transaction(function () use ($productId, $arrivedQuantity) {
            $product = Product::lockForUpdate()->findOrFail($productId);

            $product->stock_quantity += $arrivedQuantity;
            $product->expected_quantity = max(0, $product->expected_quantity - $arrivedQuantity);
            $product->save();

            // Get pending preorders in FIFO order
            $preorders = Preorder::where('product_id', $productId)
                ->where('status', 'pending')
                ->orderBy('created_at')
                ->get();

            $fulfilled = 0;
            $remainingStock = $arrivedQuantity;

            foreach ($preorders as $preorder) {
                if ($remainingStock < $preorder->quantity) {
                    break;
                }

                $this->convertPreorderToOrder($preorder);
                $remainingStock -= $preorder->quantity;
                $fulfilled++;
            }

            return [
                'success' => true,
                'arrived_quantity' => $arrivedQuantity,
                'preorders_fulfilled' => $fulfilled,
                'remaining_stock' => $remainingStock,
            ];
        });
    }

    private function convertPreorderToOrder(Preorder $preorder): Order
    {
        $order = Order::create([
            'user_id' => $preorder->user_id,
            'preorder_id' => $preorder->id,
            'status' => 'pending',
        ]);

        $preorder->update(['status' => 'converted']);

        $product = Product::find($preorder->product_id);
        $product->decrement('preorder_count', $preorder->quantity);
        $product->decrement('stock_quantity', $preorder->quantity);

        $preorder->user->notify(new PreorderReadyNotification($preorder, $order));

        return $order;
    }

    public function cancelPreorder(int $preorderId): array
    {
        $preorder = Preorder::findOrFail($preorderId);

        if ($preorder->status !== 'pending') {
            return [
                'success' => false,
                'message' => 'Preorder cannot be cancelled',
            ];
        }

        $preorder->update(['status' => 'cancelled']);

        Product::where('id', $preorder->product_id)
            ->decrement('preorder_count', $preorder->quantity);

        return [
            'success' => true,
        ];
    }
}
