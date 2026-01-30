<?php

namespace App\Services;

use App\Models\Order;
use App\Exceptions\InvalidDeliveryStatusException;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\DB;

class DeliveryStatusService
{
    private const VALID_STATUSES = [
        'pending',
        'processing',
        'shipped',
        'out_for_delivery',
        'delivered',
        'cancelled'
    ];

    private const STATUS_HIERARCHY = [
        'pending' => 0,
        'processing' => 1,
        'shipped' => 2,
        'out_for_delivery' => 3,
        'delivered' => 4,
        'cancelled' => 5
    ];

    public function __construct(
        private readonly Order $orderModel
    ) {}

    public function updateDeliveryStatus(Order $order, string $newStatus): Order
    {
        $this->validateStatus($newStatus);
        
        $currentStatus = $order->delivery_status;
        
        if ($this->isValidTransition($currentStatus, $newStatus)) {
            return $this->performStatusUpdate($order, $newStatus);
        }

        throw new InvalidDeliveryStatusException(
            "Cannot transition from {$currentStatus} to {$newStatus}"
        );
    }

    public function canTransitionTo(Order $order, string $targetStatus): bool
    {
        $this->validateStatus($targetStatus);
        
        return $this->isValidTransition($order->delivery_status, $targetStatus);
    }

    public function getAvailableTransitions(Order $order): array
    {
        $currentStatus = $order->delivery_status;
        $availableStatuses = [];

        foreach (self::VALID_STATUSES as $status) {
            if ($this->isValidTransition($currentStatus, $status)) {
                $availableStatuses[] = $status;
            }
        }

        return $availableStatuses;
    }

    private function validateStatus(string $status): void
    {
        if (!in_array($status, self::VALID_STATUSES)) {
            throw new InvalidDeliveryStatusException("Invalid delivery status: {$status}");
        }
    }

    private function isValidTransition(string $currentStatus, string $newStatus): bool
    {
        if ($currentStatus === $newStatus) {
            return false;
        }

        if ($newStatus === 'cancelled') {
            return !in_array($currentStatus, ['delivered', 'cancelled']);
        }

        if ($currentStatus === 'cancelled') {
            return false;
        }

        $currentHierarchy = self::STATUS_HIERARCHY[$currentStatus];
        $newHierarchy = self::STATUS_HIERARCHY[$newStatus];

        if ($currentStatus === 'delivered' && $newStatus === 'shipped') {
            return true;
        }

        return $newHierarchy > $currentHierarchy;
    }

    private function performStatusUpdate(Order $order, string $newStatus): Order
    {
        return DB::transaction(function () use ($order, $newStatus) {
            $order->delivery_status = $newStatus;
            $order->status_updated_at = now();
            $order->save();

            $this->logStatusChange($order, $newStatus);
            
            return $order->fresh();
        });
    }

    private function logStatusChange(Order $order, string $newStatus): void
    {
        Log::info('Delivery status updated', [
            'order_id' => $order->id,
            'new_status' => $newStatus,
            'updated_by' => auth()->id(),
            'timestamp' => now()
        ]);
    }
}