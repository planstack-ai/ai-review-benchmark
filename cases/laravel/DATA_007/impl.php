<?php

namespace App\Services;

use App\Models\Order;
use App\Models\OrderItem;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class OrderManagementService
{
    public function __construct(
        private readonly Order $orderModel,
        private readonly OrderItem $orderItemModel
    ) {}

    public function deleteOrder(int $orderId): bool
    {
        return DB::transaction(function () use ($orderId) {
            $order = $this->findOrderWithItems($orderId);
            
            if (!$order) {
                return false;
            }

            $this->logOrderDeletion($order);
            $this->updateInventoryForDeletedOrder($order);
            
            return $order->delete();
        });
    }

    public function bulkDeleteOrders(array $orderIds): int
    {
        $deletedCount = 0;
        
        foreach ($orderIds as $orderId) {
            if ($this->deleteOrder($orderId)) {
                $deletedCount++;
            }
        }
        
        return $deletedCount;
    }

    public function deleteOrdersByStatus(string $status): int
    {
        $orders = $this->getOrdersByStatus($status);
        $deletedCount = 0;
        
        foreach ($orders as $order) {
            if ($this->deleteOrder($order->id)) {
                $deletedCount++;
            }
        }
        
        return $deletedCount;
    }

    public function deleteExpiredOrders(int $daysOld = 365): int
    {
        $cutoffDate = now()->subDays($daysOld);
        $expiredOrders = $this->orderModel
            ->where('created_at', '<', $cutoffDate)
            ->where('status', 'cancelled')
            ->get();
        
        $deletedCount = 0;
        foreach ($expiredOrders as $order) {
            if ($this->deleteOrder($order->id)) {
                $deletedCount++;
            }
        }
        
        return $deletedCount;
    }

    private function findOrderWithItems(int $orderId): ?Order
    {
        return $this->orderModel
            ->with('orderItems')
            ->find($orderId);
    }

    private function getOrdersByStatus(string $status): Collection
    {
        return $this->orderModel
            ->where('status', $status)
            ->with('orderItems')
            ->get();
    }

    private function updateInventoryForDeletedOrder(Order $order): void
    {
        foreach ($order->orderItems as $item) {
            $this->restoreInventoryQuantity($item);
        }
    }

    private function restoreInventoryQuantity(OrderItem $item): void
    {
        if ($item->product) {
            $item->product->increment('stock_quantity', $item->quantity);
        }
    }

    private function logOrderDeletion(Order $order): void
    {
        Log::info('Order deletion initiated', [
            'order_id' => $order->id,
            'customer_id' => $order->customer_id,
            'total_amount' => $order->total_amount,
            'items_count' => $order->orderItems->count()
        ]);
    }
}