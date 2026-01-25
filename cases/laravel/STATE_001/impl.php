<?php

declare(strict_types=1);

namespace App\Services;

use App\Constants\OrderStatus;
use App\Models\Order;
use App\Models\OrderStatusHistory;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class OrderStateService
{
    private const VALID_TRANSITIONS = [
        OrderStatus::PENDING => [OrderStatus::PAID, OrderStatus::CANCELLED],
        OrderStatus::PAID => [OrderStatus::PROCESSING, OrderStatus::REFUNDED],
        OrderStatus::PROCESSING => [OrderStatus::SHIPPED],
        OrderStatus::SHIPPED => [OrderStatus::DELIVERED],
        OrderStatus::DELIVERED => [],
        OrderStatus::CANCELLED => [],
        OrderStatus::REFUNDED => [],
    ];

    public function transition(int $orderId, string $toStatus, ?string $notes = null): array
    {
        return DB::transaction(function () use ($orderId, $toStatus, $notes) {
            $order = Order::lockForUpdate()->findOrFail($orderId);

            // BUG: Validates transition but then allows any status to be set
            // The validation result is not used to prevent invalid transitions
            $isValid = $this->isValidTransition($order->status, $toStatus);

            if (!$isValid) {
                \Log::warning("Invalid transition attempted: {$order->status} -> {$toStatus}");
            }

            // BUG: Status is updated regardless of validation result
            $fromStatus = $order->status;
            $order->status = $toStatus;
            $order->save();

            OrderStatusHistory::create([
                'order_id' => $orderId,
                'from_status' => $fromStatus,
                'to_status' => $toStatus,
                'changed_by' => Auth::id(),
                'notes' => $notes,
            ]);

            return [
                'success' => true,
                'order' => $order,
                'transition' => "{$fromStatus} → {$toStatus}",
            ];
        });
    }

    public function markAsPaid(int $orderId): array
    {
        return $this->transition($orderId, OrderStatus::PAID, 'Payment confirmed');
    }

    public function startProcessing(int $orderId): array
    {
        return $this->transition($orderId, OrderStatus::PROCESSING, 'Picked for fulfillment');
    }

    public function markAsShipped(int $orderId, string $trackingNumber): array
    {
        return $this->transition($orderId, OrderStatus::SHIPPED, "Tracking: {$trackingNumber}");
    }

    public function markAsDelivered(int $orderId): array
    {
        return $this->transition($orderId, OrderStatus::DELIVERED, 'Delivery confirmed');
    }

    public function cancel(int $orderId, string $reason): array
    {
        $order = Order::findOrFail($orderId);

        $targetStatus = $order->status === OrderStatus::PAID
            ? OrderStatus::REFUNDED
            : OrderStatus::CANCELLED;

        return $this->transition($orderId, $targetStatus, "Cancelled: {$reason}");
    }

    private function isValidTransition(string $from, string $to): bool
    {
        $allowedTransitions = self::VALID_TRANSITIONS[$from] ?? [];

        return in_array($to, $allowedTransitions, true);
    }
}
