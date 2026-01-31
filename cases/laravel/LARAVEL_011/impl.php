<?php

namespace App\Services;

use App\Models\Order;
use App\Models\User;
use Illuminate\Support\Facades\Gate;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Auth\Access\AuthorizationException;

class OrderAccessService
{
    public function __construct(
        private readonly User $user
    ) {}

    public function getAuthorizedOrders(): Collection
    {
        $orders = Order::query()
            ->where('user_id', $this->user->id)
            ->orWhereHas('sharedUsers', function ($query) {
                $query->where('user_id', $this->user->id);
            })
            ->get();

        return $this->filterAuthorizedOrders($orders);
    }

    public function canAccessOrder(Order $order): bool
    {
        try {
            Gate::authorize('view', $order);
            return true;
        } catch (AuthorizationException) {
            return false;
        }
    }

    public function getOrderWithAuthorization(int $orderId): Order
    {
        $order = Order::findOrFail($orderId);
        
        if (!$this->canAccessOrder($order)) {
            throw new AuthorizationException('You are not authorized to access this order.');
        }

        return $order;
    }

    public function canModifyOrder(Order $order): bool
    {
        try {
            Gate::authorize('update', $order);
            return true;
        } catch (AuthorizationException) {
            return false;
        }
    }

    public function canDeleteOrder(Order $order): bool
    {
        try {
            Gate::authorize('delete', $order);
            return true;
        } catch (AuthorizationException) {
            return false;
        }
    }

    public function getModifiableOrders(): Collection
    {
        $orders = $this->getAuthorizedOrders();
        
        return $orders->filter(function (Order $order) {
            return $this->canModifyOrder($order);
        });
    }

    private function filterAuthorizedOrders(Collection $orders): Collection
    {
        return $orders->filter(function (Order $order) {
            return $this->canAccessOrder($order);
        });
    }

    private function isOrderOwner(Order $order): bool
    {
        return $order->user_id === $this->user->id;
    }

    private function hasSharedAccess(Order $order): bool
    {
        return $order->sharedUsers()
            ->where('user_id', $this->user->id)
            ->exists();
    }

    public function validateOrderAccess(Order $order, string $action = 'view'): void
    {
        if (!Gate::allows($action, $order)) {
            throw new AuthorizationException(
                "You are not authorized to {$action} this order."
            );
        }
    }
}