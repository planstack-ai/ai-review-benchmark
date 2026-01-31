<?php

namespace App\Services;

use App\Models\Order;
use App\Models\User;
use App\Mail\OrderConfirmationMail;
use App\Mail\OrderStatusUpdateMail;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Facades\Log;

class OrderNotificationService
{
    public function __construct(
        private readonly User $user
    ) {}

    public function sendOrderConfirmation(Order $order): bool
    {
        try {
            $this->validateOrder($order);
            
            $emailData = $this->prepareConfirmationData($order);
            
            Mail::to($this->user->email)->send(
                new OrderConfirmationMail($emailData)
            );
            
            $this->logNotification($order, 'confirmation');
            
            return true;
        } catch (\Exception $e) {
            Log::error('Failed to send order confirmation', [
                'order_id' => $order->id,
                'error' => $e->getMessage()
            ]);
            
            return false;
        }
    }

    public function sendStatusUpdate(Order $order, string $status): bool
    {
        try {
            $this->validateOrder($order);
            $this->validateStatus($status);
            
            $emailData = $this->prepareStatusUpdateData($order, $status);
            
            Mail::to($this->user->email)->send(
                new OrderStatusUpdateMail($emailData)
            );
            
            $this->logNotification($order, 'status_update');
            
            return true;
        } catch (\Exception $e) {
            Log::error('Failed to send status update', [
                'order_id' => $order->id,
                'status' => $status,
                'error' => $e->getMessage()
            ]);
            
            return false;
        }
    }

    private function validateOrder(Order $order): void
    {
        if (!$order->exists) {
            throw new \InvalidArgumentException('Order does not exist');
        }
        
        if (!$order->user) {
            throw new \InvalidArgumentException('Order must have an associated user');
        }
    }

    private function validateStatus(string $status): void
    {
        $validStatuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled'];
        
        if (!in_array($status, $validStatuses)) {
            throw new \InvalidArgumentException('Invalid order status');
        }
    }

    private function prepareConfirmationData(Order $order): array
    {
        return [
            'order_number' => $order->order_number,
            'customer_name' => $order->user->name,
            'total_amount' => $order->total_amount,
            'items' => $order->items->toArray(),
            'shipping_address' => $order->shipping_address,
            'estimated_delivery' => $order->estimated_delivery_date
        ];
    }

    private function prepareStatusUpdateData(Order $order, string $status): array
    {
        return [
            'order_number' => $order->order_number,
            'customer_name' => $order->user->name,
            'new_status' => $status,
            'tracking_number' => $order->tracking_number,
            'status_message' => $this->getStatusMessage($status)
        ];
    }

    private function getStatusMessage(string $status): string
    {
        return match ($status) {
            'pending' => 'Your order has been received and is being processed.',
            'processing' => 'Your order is currently being prepared for shipment.',
            'shipped' => 'Your order has been shipped and is on its way to you.',
            'delivered' => 'Your order has been successfully delivered.',
            'cancelled' => 'Your order has been cancelled as requested.',
            default => 'Your order status has been updated.'
        };
    }

    private function logNotification(Order $order, string $type): void
    {
        Log::info('Order notification sent', [
            'order_id' => $order->id,
            'type' => $type,
            'recipient' => $this->user->email
        ]);
    }
}