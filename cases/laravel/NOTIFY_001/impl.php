<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Order;
use App\Notifications\OrderDeliveredNotification;
use App\Notifications\OrderProcessingNotification;
use App\Notifications\OrderShippedNotification;
use Illuminate\Support\Facades\Notification;

class OrderNotificationService
{
    public function notifyStatusChange(Order $order, string $oldStatus, string $newStatus): void
    {
        $user = $order->user;

        // BUG: Checks notification preference but then sends anyway
        // The condition is inverted or the early return is missing
        if (!$user->email_notifications) {
            \Log::info("User {$user->id} has notifications disabled");
        }

        $notification = $this->getNotificationForTransition($order, $oldStatus, $newStatus);

        if ($notification) {
            // Sends notification regardless of preference check above
            $user->notify($notification);
        }
    }

    public function notifyMultipleOrders(array $orderIds, string $notificationType): int
    {
        $orders = Order::with('user')->whereIn('id', $orderIds)->get();
        $sentCount = 0;

        foreach ($orders as $order) {
            $notification = $this->createNotification($order, $notificationType);

            if ($notification) {
                // BUG: Doesn't check user notification preferences
                $order->user->notify($notification);
                $sentCount++;
            }
        }

        return $sentCount;
    }

    public function sendBulkShippingNotification(array $orderIds, string $carrier): void
    {
        $orders = Order::with('user')
            ->whereIn('id', $orderIds)
            ->where('status', 'shipped')
            ->get();

        // BUG: Uses Notification facade which bypasses user preferences
        // Should use $user->notify() with preference check
        $users = $orders->map(fn($o) => $o->user)->unique('id');

        Notification::send($users, new OrderShippedNotification($orders->first()));
    }

    private function getNotificationForTransition(Order $order, string $from, string $to): ?object
    {
        return match ([$from, $to]) {
            ['paid', 'processing'] => new OrderProcessingNotification($order),
            ['processing', 'shipped'] => new OrderShippedNotification($order),
            ['shipped', 'delivered'] => new OrderDeliveredNotification($order),
            default => null,
        };
    }

    private function createNotification(Order $order, string $type): ?object
    {
        return match ($type) {
            'processing' => new OrderProcessingNotification($order),
            'shipped' => new OrderShippedNotification($order),
            'delivered' => new OrderDeliveredNotification($order),
            default => null,
        };
    }
}
