<?php

namespace App\Services;

use App\Models\Order;
use App\Models\User;
use Illuminate\Database\Eloquent\ModelNotFoundException;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Str;

class OrderRetrievalService
{
    public function __construct(
        private readonly Order $orderModel
    ) {}

    public function findOrderByIdentifier(string $identifier): Order
    {
        $order = $this->attemptOrderRetrieval($identifier);
        
        if (!$order) {
            Log::warning('Order not found', ['identifier' => $identifier]);
            throw new ModelNotFoundException('Order not found');
        }

        return $this->enrichOrderData($order);
    }

    public function getOrdersForUser(User $user, array $filters = []): array
    {
        $query = $this->orderModel->where('user_id', $user->id);
        
        if (isset($filters['status'])) {
            $query->where('status', $filters['status']);
        }
        
        if (isset($filters['date_from'])) {
            $query->where('created_at', '>=', $filters['date_from']);
        }
        
        return $query->with(['items', 'payments'])
                    ->orderBy('created_at', 'desc')
                    ->get()
                    ->map(fn($order) => $this->enrichOrderData($order))
                    ->toArray();
    }

    public function validateOrderAccess(Order $order, User $user): bool
    {
        if ($order->user_id === $user->id) {
            return true;
        }

        if ($user->hasRole('admin')) {
            return true;
        }

        if ($this->isSharedOrder($order, $user)) {
            return true;
        }

        return false;
    }

    private function attemptOrderRetrieval(string $identifier): ?Order
    {
        if ($this->isUuidFormat($identifier)) {
            return $this->orderModel->where('uuid', $identifier)->first();
        }

        if (is_numeric($identifier)) {
            return $this->orderModel->find($identifier);
        }

        return null;
    }

    private function enrichOrderData(Order $order): Order
    {
        $order->load(['user', 'items.product', 'payments', 'shipping']);
        
        $order->total_amount = $this->calculateOrderTotal($order);
        $order->status_label = $this->getStatusLabel($order->status);
        $order->estimated_delivery = $this->calculateEstimatedDelivery($order);
        
        return $order;
    }

    private function isUuidFormat(string $value): bool
    {
        return Str::isUuid($value);
    }

    private function calculateOrderTotal(Order $order): float
    {
        return $order->items->sum(function ($item) {
            return $item->quantity * $item->price;
        }) + ($order->shipping_cost ?? 0) + ($order->tax_amount ?? 0);
    }

    private function getStatusLabel(string $status): string
    {
        return match($status) {
            'pending' => 'Pending Payment',
            'processing' => 'Processing',
            'shipped' => 'Shipped',
            'delivered' => 'Delivered',
            'cancelled' => 'Cancelled',
            default => 'Unknown Status'
        };
    }

    private function calculateEstimatedDelivery(Order $order): ?string
    {
        if ($order->status === 'shipped' && $order->shipping) {
            return $order->shipping->estimated_delivery_date;
        }

        return null;
    }

    private function isSharedOrder(Order $order, User $user): bool
    {
        return DB::table('order_shares')
                 ->where('order_id', $order->id)
                 ->where('shared_with_user_id', $user->id)
                 ->where('expires_at', '>', now())
                 ->exists();
    }
}