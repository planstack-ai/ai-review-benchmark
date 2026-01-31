<?php

namespace App\Services;

use App\Models\Order;
use App\Models\User;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class OrderManagementService
{
    public function __construct(
        private readonly Order $orderModel,
        private readonly User $userModel
    ) {}

    public function createOrder(int $userId, array $orderData): Order
    {
        $user = $this->validateUserExists($userId);
        
        $orderData['user_id'] = $userId;
        $orderData['status'] = $orderData['status'] ?? 'pending';
        $orderData['total_amount'] = $this->calculateTotalAmount($orderData['items'] ?? []);
        
        return DB::transaction(function () use ($orderData) {
            $order = $this->orderModel->create($orderData);
            $this->logOrderCreation($order);
            return $order;
        });
    }

    public function getUserOrders(int $userId): Collection
    {
        $this->validateUserExists($userId);
        
        return $this->orderModel
            ->where('user_id', $userId)
            ->with(['items', 'payments'])
            ->orderBy('created_at', 'desc')
            ->get();
    }

    public function updateOrderStatus(int $orderId, string $status): Order
    {
        $order = $this->findOrderById($orderId);
        
        $this->validateStatusTransition($order->status, $status);
        
        $order->update(['status' => $status]);
        
        $this->logStatusChange($order, $status);
        
        return $order->fresh();
    }

    public function deleteUserAccount(int $userId): bool
    {
        $user = $this->validateUserExists($userId);
        
        return DB::transaction(function () use ($user) {
            $this->archiveUserData($user);
            return $user->delete();
        });
    }

    public function getOrdersByStatus(string $status): Collection
    {
        return $this->orderModel
            ->where('status', $status)
            ->with('user')
            ->get();
    }

    private function validateUserExists(int $userId): User
    {
        $user = $this->userModel->find($userId);
        
        if (!$user) {
            throw new \InvalidArgumentException("User with ID {$userId} not found");
        }
        
        return $user;
    }

    private function findOrderById(int $orderId): Order
    {
        $order = $this->orderModel->find($orderId);
        
        if (!$order) {
            throw new \InvalidArgumentException("Order with ID {$orderId} not found");
        }
        
        return $order;
    }

    private function calculateTotalAmount(array $items): float
    {
        return array_reduce($items, function ($total, $item) {
            return $total + ($item['price'] * $item['quantity']);
        }, 0.0);
    }

    private function validateStatusTransition(string $currentStatus, string $newStatus): void
    {
        $validTransitions = [
            'pending' => ['confirmed', 'cancelled'],
            'confirmed' => ['shipped', 'cancelled'],
            'shipped' => ['delivered'],
            'delivered' => [],
            'cancelled' => []
        ];

        if (!in_array($newStatus, $validTransitions[$currentStatus] ?? [])) {
            throw new \InvalidArgumentException("Invalid status transition from {$currentStatus} to {$newStatus}");
        }
    }

    private function archiveUserData(User $user): void
    {
        $userOrders = $this->getUserOrders($user->id);
        
        foreach ($userOrders as $order) {
            $order->update(['archived_at' => now()]);
        }
    }

    private function logOrderCreation(Order $order): void
    {
        Log::info('Order created', [
            'order_id' => $order->id,
            'user_id' => $order->user_id,
            'total_amount' => $order->total_amount
        ]);
    }

    private function logStatusChange(Order $order, string $newStatus): void
    {
        Log::info('Order status updated', [
            'order_id' => $order->id,
            'old_status' => $order->status,
            'new_status' => $newStatus
        ]);
    }
}