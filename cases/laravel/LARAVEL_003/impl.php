<?php

namespace App\Services;

use App\Events\OrderCreated;
use App\Events\OrderInventoryUpdated;
use App\Events\OrderValidated;
use App\Models\Order;
use App\Models\Product;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Event;
use Illuminate\Support\Facades\Log;

class OrderProcessingService
{
    public function __construct(
        private readonly InventoryService $inventoryService,
        private readonly ValidationService $validationService,
        private readonly NotificationService $notificationService
    ) {}

    public function processOrder(array $orderData): Order
    {
        return DB::transaction(function () use ($orderData) {
            $order = $this->createOrder($orderData);
            $this->triggerOrderEvents($order);
            
            return $order;
        });
    }

    private function createOrder(array $orderData): Order
    {
        $order = Order::create([
            'customer_id' => $orderData['customer_id'],
            'total_amount' => $orderData['total_amount'],
            'status' => 'pending',
            'items' => $orderData['items'],
        ]);

        foreach ($orderData['items'] as $item) {
            $order->items()->create([
                'product_id' => $item['product_id'],
                'quantity' => $item['quantity'],
                'price' => $item['price'],
            ]);
        }

        return $order;
    }

    private function triggerOrderEvents(Order $order): void
    {
        Event::dispatch(new OrderCreated($order));
        Event::dispatch(new OrderInventoryUpdated($order));
        Event::dispatch(new OrderValidated($order));
    }

    public function validateOrderItems(Order $order): bool
    {
        foreach ($order->items as $item) {
            if (!$this->isProductAvailable($item->product_id, $item->quantity)) {
                $this->markOrderAsInvalid($order, 'Insufficient inventory');
                return false;
            }

            if (!$this->validatePricing($item)) {
                $this->markOrderAsInvalid($order, 'Invalid pricing');
                return false;
            }
        }

        $order->update(['status' => 'validated']);
        return true;
    }

    private function isProductAvailable(int $productId, int $quantity): bool
    {
        $product = Product::find($productId);
        return $product && $product->stock_quantity >= $quantity;
    }

    private function validatePricing(object $item): bool
    {
        $product = Product::find($item->product_id);
        return $product && abs($product->price - $item->price) < 0.01;
    }

    private function markOrderAsInvalid(Order $order, string $reason): void
    {
        $order->update([
            'status' => 'invalid',
            'validation_error' => $reason,
        ]);

        Log::warning("Order {$order->id} marked as invalid: {$reason}");
    }

    public function updateInventory(Order $order): void
    {
        foreach ($order->items as $item) {
            $this->inventoryService->reserveStock(
                $item->product_id,
                $item->quantity
            );
        }

        $order->update(['inventory_reserved' => true]);
    }

    public function finalizeOrder(Order $order): void
    {
        if ($order->status === 'validated' && $order->inventory_reserved) {
            $order->update(['status' => 'confirmed']);
            $this->notificationService->sendOrderConfirmation($order);
        }
    }
}