<?php

namespace App\Services;

use App\Models\Order;
use App\Models\User;
use App\Services\PaymentService;
use App\Services\InventoryService;
use App\Services\NotificationService;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use InvalidArgumentException;

class OrderProcessingService
{
    public function __construct(
        private PaymentService $paymentService,
        private InventoryService $inventoryService,
        private NotificationService $notificationService
    ) {}

    public function processOrder(User $user, array $orderData): Order
    {
        $this->validateOrderData($orderData);
        
        $order = $this->createOrderFromData($user, $orderData);
        
        return $this->saveOrderWithPayment($order, $orderData['payment_method']);
    }

    private function validateOrderData(array $orderData): void
    {
        if (empty($orderData['items'])) {
            throw new InvalidArgumentException('Order must contain at least one item');
        }

        if (empty($orderData['payment_method'])) {
            throw new InvalidArgumentException('Payment method is required');
        }

        if (!isset($orderData['total_amount']) || $orderData['total_amount'] <= 0) {
            throw new InvalidArgumentException('Invalid order total amount');
        }
    }

    private function createOrderFromData(User $user, array $orderData): Order
    {
        $order = new Order();
        $order->user_id = $user->id;
        $order->total_amount = $orderData['total_amount'];
        $order->status = 'pending';
        $order->order_number = $this->generateOrderNumber();
        
        return $order;
    }

    private function saveOrderWithPayment(Order $order, string $paymentMethod): Order
    {
        return DB::transaction(function () use ($order, $paymentMethod) {
            $order->save();
            
            $this->reserveInventory($order);
            
            $paymentResult = $this->chargePayment($order, $paymentMethod);
            
            if (!$paymentResult['success']) {
                throw new \Exception('Payment processing failed: ' . $paymentResult['error']);
            }
            
            $order->payment_id = $paymentResult['payment_id'];
            $order->status = 'confirmed';
            $order->save();
            
            $this->sendConfirmationNotification($order);
            
            return $order;
        });
    }

    private function reserveInventory(Order $order): void
    {
        foreach ($order->items as $item) {
            if (!$this->inventoryService->reserveItem($item->product_id, $item->quantity)) {
                throw new \Exception("Insufficient inventory for product {$item->product_id}");
            }
        }
    }

    private function chargePayment(Order $order, string $paymentMethod): array
    {
        try {
            $result = $this->paymentService->charge([
                'amount' => $order->total_amount,
                'payment_method' => $paymentMethod,
                'order_id' => $order->id,
                'description' => "Order #{$order->order_number}"
            ]);

            Log::info('Payment processed successfully', [
                'order_id' => $order->id,
                'payment_id' => $result['payment_id']
            ]);

            return $result;
        } catch (\Exception $e) {
            Log::error('Payment processing failed', [
                'order_id' => $order->id,
                'error' => $e->getMessage()
            ]);

            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }

    private function sendConfirmationNotification(Order $order): void
    {
        $this->notificationService->sendOrderConfirmation($order);
    }

    private function generateOrderNumber(): string
    {
        return 'ORD-' . strtoupper(uniqid());
    }
}