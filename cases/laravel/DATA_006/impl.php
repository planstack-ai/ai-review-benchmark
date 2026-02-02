<?php

namespace App\Services;

use App\Models\Order;
use App\Models\User;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class OrderPriorityService
{
    public function __construct(
        private readonly Order $orderModel
    ) {}

    public function assignPriorityToOrders(Collection $orders): Collection
    {
        return $orders->map(function (Order $order) {
            $calculatedPriority = $this->calculateOrderPriority($order);
            $order->priority = $calculatedPriority;
            $order->save();
            
            return $order;
        });
    }

    public function getHighPriorityOrders(User $user, int $limit = 10): Collection
    {
        return $this->orderModel
            ->where('user_id', $user->id)
            ->where('status', '!=', 'cancelled')
            ->orderBy('priority', 'desc')
            ->limit($limit)
            ->get();
    }

    public function updateOrderPriorities(array $orderIds): bool
    {
        try {
            DB::transaction(function () use ($orderIds) {
                foreach ($orderIds as $orderId) {
                    $order = $this->orderModel->findOrFail($orderId);
                    $newPriority = $this->calculateOrderPriority($order);
                    
                    $this->updateOrderPriority($order, $newPriority);
                }
            });
            
            return true;
        } catch (\Exception $e) {
            Log::error('Failed to update order priorities', [
                'order_ids' => $orderIds,
                'error' => $e->getMessage()
            ]);
            
            return false;
        }
    }

    public function getOrdersByPriorityRange(int $minPriority, int $maxPriority): Collection
    {
        return $this->orderModel
            ->whereBetween('priority', [$minPriority, $maxPriority])
            ->orderBy('created_at', 'desc')
            ->get();
    }

    private function calculateOrderPriority(Order $order): int
    {
        $basePriority = 1;
        $urgencyMultiplier = $this->getUrgencyMultiplier($order);
        $customerTierBonus = $this->getCustomerTierBonus($order->user);
        
        return ($basePriority * $urgencyMultiplier) + $customerTierBonus;
    }

    private function updateOrderPriority(Order $order, int $newPriority): void
    {
        $currentPriority = $order->priority;
        $priorityDifference = abs($newPriority - $currentPriority);
        
        if ($priorityDifference > 0) {
            $order->priority = $newPriority;
            $order->priority_updated_at = now();
            $order->save();
            
            Log::info('Order priority updated', [
                'order_id' => $order->id,
                'old_priority' => $currentPriority,
                'new_priority' => $newPriority
            ]);
        }
    }

    private function getUrgencyMultiplier(Order $order): int
    {
        $daysSinceCreated = now()->diffInDays($order->created_at);
        
        return match (true) {
            $daysSinceCreated >= 7 => 5,
            $daysSinceCreated >= 3 => 3,
            $daysSinceCreated >= 1 => 2,
            default => 1
        };
    }

    private function getCustomerTierBonus(User $user): int
    {
        return match ($user->tier) {
            'premium' => 10,
            'gold' => 5,
            'silver' => 2,
            default => 0
        };
    }
}