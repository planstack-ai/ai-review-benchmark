<?php

namespace App\Observers;

use App\Models\Order;
use App\Models\Product;
use App\Models\InventoryLog;
use Illuminate\Support\Facades\Log;

/**
 * Observer for handling Order model events.
 *
 * BUG: This Observer doesn't set $afterCommit = true, so the created() method
 * fires BEFORE the transaction commits. If the transaction rolls back,
 * inventory has already been decremented but the order won't exist.
 */
class OrderObserver
{
    /**
     * Handle the Order "created" event.
     *
     * This method decrements inventory when an order is created.
     * BUG: Without $afterCommit = true, this runs before the transaction commits.
     * If the transaction rolls back (e.g., payment fails), inventory is incorrectly reduced.
     */
    public function created(Order $order): void
    {
        if (!$this->shouldProcessInventory($order)) {
            return;
        }

        foreach ($order->items as $item) {
            $this->decrementInventory($item->product_id, $item->quantity, $order);
        }

        Log::info('Inventory updated for order', [
            'order_id' => $order->id,
            'items_count' => $order->items->count(),
        ]);
    }

    /**
     * Handle the Order "updated" event.
     */
    public function updated(Order $order): void
    {
        if ($order->wasChanged('status') && $order->status === 'cancelled') {
            $this->restoreInventory($order);
        }
    }

    /**
     * Handle the Order "deleted" event.
     */
    public function deleted(Order $order): void
    {
        if ($order->status !== 'cancelled') {
            $this->restoreInventory($order);
        }
    }

    /**
     * Determine if inventory should be processed for this order.
     */
    private function shouldProcessInventory(Order $order): bool
    {
        $processableStatuses = ['confirmed', 'paid', 'pending'];

        return in_array($order->status, $processableStatuses);
    }

    /**
     * Decrement inventory for a product.
     */
    private function decrementInventory(int $productId, int $quantity, Order $order): void
    {
        $product = Product::find($productId);

        if (!$product) {
            Log::warning('Product not found for inventory update', [
                'product_id' => $productId,
                'order_id' => $order->id,
            ]);
            return;
        }

        if ($product->stock_quantity < $quantity) {
            Log::error('Insufficient stock for inventory update', [
                'product_id' => $productId,
                'available' => $product->stock_quantity,
                'requested' => $quantity,
            ]);
            throw new \Exception("Insufficient stock for product {$product->name}");
        }

        $product->decrement('stock_quantity', $quantity);

        InventoryLog::create([
            'product_id' => $productId,
            'order_id' => $order->id,
            'quantity_change' => -$quantity,
            'previous_quantity' => $product->stock_quantity + $quantity,
            'new_quantity' => $product->stock_quantity,
            'reason' => 'order_created',
        ]);
    }

    /**
     * Restore inventory when an order is cancelled or deleted.
     */
    private function restoreInventory(Order $order): void
    {
        foreach ($order->items as $item) {
            $product = Product::find($item->product_id);

            if ($product) {
                $product->increment('stock_quantity', $item->quantity);

                InventoryLog::create([
                    'product_id' => $item->product_id,
                    'order_id' => $order->id,
                    'quantity_change' => $item->quantity,
                    'previous_quantity' => $product->stock_quantity - $item->quantity,
                    'new_quantity' => $product->stock_quantity,
                    'reason' => 'order_cancelled',
                ]);
            }
        }

        Log::info('Inventory restored for cancelled order', [
            'order_id' => $order->id,
        ]);
    }
}
