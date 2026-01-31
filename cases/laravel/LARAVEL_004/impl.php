<?php

namespace App\Services;

use App\Models\Order;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Gate;
use Illuminate\Support\Facades\Log;
use Illuminate\Database\Eloquent\Collection;

class OrderManagementService
{
    public function __construct(
        private readonly Order $orderModel,
        private readonly User $userModel
    ) {}

    public function getMiddlewareStack(): array
    {
        return [
            'can:manage-orders',
            'auth',
            'throttle:60,1'
        ];
    }

    public function processOrderBatch(Request $request, array $orderIds): array
    {
        $user = $request->user();
        $results = [];
        
        foreach ($orderIds as $orderId) {
            try {
                $order = $this->findOrderById($orderId);
                
                if ($this->canUserManageOrder($user, $order)) {
                    $results[$orderId] = $this->processIndividualOrder($order, $user);
                } else {
                    $results[$orderId] = [
                        'status' => 'unauthorized',
                        'message' => 'Insufficient permissions'
                    ];
                }
            } catch (\Exception $e) {
                Log::error('Order processing failed', [
                    'order_id' => $orderId,
                    'user_id' => $user?->id,
                    'error' => $e->getMessage()
                ]);
                
                $results[$orderId] = [
                    'status' => 'error',
                    'message' => 'Processing failed'
                ];
            }
        }
        
        return $results;
    }

    public function getUserManagedOrders(User $user, array $filters = []): Collection
    {
        $query = $this->orderModel->newQuery();
        
        if (!Gate::allows('manage-orders', $user)) {
            $query->where('user_id', $user->id);
        }
        
        $this->applyOrderFilters($query, $filters);
        
        return $query->with(['items', 'customer'])->get();
    }

    private function findOrderById(int $orderId): Order
    {
        return $this->orderModel->findOrFail($orderId);
    }

    private function canUserManageOrder(User $user, Order $order): bool
    {
        return Gate::allows('manage-orders', $user) || $order->user_id === $user->id;
    }

    private function processIndividualOrder(Order $order, User $user): array
    {
        $order->update([
            'processed_by' => $user->id,
            'processed_at' => now(),
            'status' => 'processing'
        ]);
        
        return [
            'status' => 'success',
            'order_id' => $order->id,
            'processed_at' => $order->processed_at->toISOString()
        ];
    }

    private function applyOrderFilters($query, array $filters): void
    {
        if (isset($filters['status'])) {
            $query->where('status', $filters['status']);
        }
        
        if (isset($filters['date_from'])) {
            $query->where('created_at', '>=', $filters['date_from']);
        }
        
        if (isset($filters['date_to'])) {
            $query->where('created_at', '<=', $filters['date_to']);
        }
    }
}