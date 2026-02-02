<?php

namespace App\Services;

use App\Jobs\NotifyOrderCreatedJob;
use App\Jobs\NotifyOrderUpdatedJob;
use App\Models\Order;
use App\Models\User;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class OrderProcessingService
{
    public function __construct(
        private readonly NotificationService $notificationService
    ) {}

    public function createOrder(User $user, array $orderData): Order
    {
        return DB::transaction(function () use ($user, $orderData) {
            $order = $this->buildOrderFromData($user, $orderData);
            $order->save();
            
            $this->processOrderItems($order, $orderData['items'] ?? []);
            $this->updateInventory($order);
            
            NotifyOrderCreatedJob::dispatch($order);
            
            Log::info('Order created successfully', ['order_id' => $order->id]);
            
            return $order;
        });
    }

    public function updateOrder(Order $order, array $updateData): Order
    {
        return DB::transaction(function () use ($order, $updateData) {
            $originalStatus = $order->status;
            
            $order->fill($this->sanitizeUpdateData($updateData));
            $order->save();
            
            if ($this->shouldUpdateItems($updateData)) {
                $this->processOrderItems($order, $updateData['items']);
                $this->updateInventory($order);
            }
            
            if ($this->hasStatusChanged($originalStatus, $order->status)) {
                NotifyOrderUpdatedJob::dispatch($order, $originalStatus);
            }
            
            return $order->fresh();
        });
    }

    private function buildOrderFromData(User $user, array $data): Order
    {
        return new Order([
            'user_id' => $user->id,
            'total_amount' => $data['total_amount'],
            'currency' => $data['currency'] ?? 'USD',
            'status' => 'pending',
            'shipping_address' => $data['shipping_address'],
            'billing_address' => $data['billing_address'] ?? $data['shipping_address'],
        ]);
    }

    private function processOrderItems(Order $order, array $items): void
    {
        $order->items()->delete();
        
        foreach ($items as $itemData) {
            $order->items()->create([
                'product_id' => $itemData['product_id'],
                'quantity' => $itemData['quantity'],
                'unit_price' => $itemData['unit_price'],
                'total_price' => $itemData['quantity'] * $itemData['unit_price'],
            ]);
        }
    }

    private function updateInventory(Order $order): void
    {
        foreach ($order->items as $item) {
            $product = $item->product;
            $product->decrement('stock_quantity', $item->quantity);
            
            if ($product->stock_quantity < $product->low_stock_threshold) {
                $this->notificationService->notifyLowStock($product);
            }
        }
    }

    private function sanitizeUpdateData(array $data): array
    {
        return array_intersect_key($data, array_flip([
            'status', 'shipping_address', 'billing_address', 'notes'
        ]));
    }

    private function shouldUpdateItems(array $updateData): bool
    {
        return isset($updateData['items']) && is_array($updateData['items']);
    }

    private function hasStatusChanged(string $originalStatus, string $newStatus): bool
    {
        return $originalStatus !== $newStatus;
    }
}