<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Order;
use App\Models\OrderItem;
use App\Models\Product;
use App\Models\ReturnRequest;
use Illuminate\Support\Facades\DB;

class ReturnService
{
    public function processReturn(int $orderId, int $orderItemId, int $quantity): array
    {
        return DB::transaction(function () use ($orderId, $orderItemId, $quantity) {
            $order = Order::findOrFail($orderId);

            if ($order->status !== 'delivered') {
                return [
                    'success' => false,
                    'message' => 'Only delivered orders can be returned',
                ];
            }

            if ($order->delivered_at->diffInDays(now()) > 30) {
                return [
                    'success' => false,
                    'message' => 'Return period has expired',
                ];
            }

            $orderItem = OrderItem::where('order_id', $orderId)
                ->where('id', $orderItemId)
                ->firstOrFail();

            if ($quantity > $orderItem->quantity) {
                return [
                    'success' => false,
                    'message' => 'Return quantity exceeds purchased quantity',
                ];
            }

            // BUG: Stock is restored when return is requested, not when approved
            // Should only restore stock after return is approved and item received
            $product = Product::findOrFail($orderItem->product_id);
            $product->increment('stock_quantity', $quantity);

            $return = ReturnRequest::create([
                'order_id' => $orderId,
                'order_item_id' => $orderItemId,
                'quantity' => $quantity,
                'status' => 'pending',
            ]);

            return [
                'success' => true,
                'return' => $return,
            ];
        });
    }

    public function approveReturn(int $returnId): array
    {
        $return = ReturnRequest::findOrFail($returnId);

        if ($return->status !== 'pending') {
            return [
                'success' => false,
                'message' => 'Return is not pending approval',
            ];
        }

        $return->update(['status' => 'approved']);

        return [
            'success' => true,
            'return' => $return,
        ];
    }

    public function completeReturn(int $returnId): array
    {
        $return = ReturnRequest::findOrFail($returnId);

        if ($return->status !== 'approved') {
            return [
                'success' => false,
                'message' => 'Return must be approved first',
            ];
        }

        $orderItem = OrderItem::findOrFail($return->order_item_id);
        $orderItem->update(['returned' => true]);

        $return->update(['status' => 'completed']);

        return [
            'success' => true,
            'return' => $return,
        ];
    }
}
