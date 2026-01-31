<?php

namespace App\Services;

use App\Models\Order;
use App\Models\Payment;
use App\Models\WebhookLog;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Exception;

class PaymentWebhookService
{
    public function __construct(
        private readonly Order $orderModel,
        private readonly Payment $paymentModel,
        private readonly WebhookLog $webhookLogModel
    ) {}

    public function processWebhook(array $payload): bool
    {
        try {
            $eventId = $payload['id'] ?? null;
            $eventType = $payload['type'] ?? null;
            $paymentData = $payload['data']['object'] ?? [];

            if (!$eventId || !$eventType || empty($paymentData)) {
                Log::warning('Invalid webhook payload received', ['payload' => $payload]);
                return false;
            }

            return DB::transaction(function () use ($eventId, $eventType, $paymentData) {
                $this->logWebhookEvent($eventId, $eventType, $paymentData);
                
                return match ($eventType) {
                    'payment_intent.succeeded' => $this->handlePaymentSuccess($paymentData),
                    'payment_intent.payment_failed' => $this->handlePaymentFailure($paymentData),
                    'payment_intent.canceled' => $this->handlePaymentCancellation($paymentData),
                    default => $this->handleUnknownEvent($eventType, $paymentData)
                };
            });
        } catch (Exception $e) {
            Log::error('Webhook processing failed', [
                'error' => $e->getMessage(),
                'payload' => $payload
            ]);
            return false;
        }
    }

    private function handlePaymentSuccess(array $paymentData): bool
    {
        $paymentIntentId = $paymentData['id'];
        $amount = $paymentData['amount'] / 100;
        $currency = $paymentData['currency'];
        $orderId = $paymentData['metadata']['order_id'] ?? null;

        if (!$orderId) {
            Log::warning('No order ID found in payment metadata', ['payment_intent' => $paymentIntentId]);
            return false;
        }

        $order = $this->orderModel->find($orderId);
        if (!$order) {
            Log::warning('Order not found for payment', ['order_id' => $orderId]);
            return false;
        }

        $this->updateOrderStatus($order, 'paid');
        $this->createPaymentRecord($order, $paymentIntentId, $amount, $currency, 'completed');

        return true;
    }

    private function handlePaymentFailure(array $paymentData): bool
    {
        $paymentIntentId = $paymentData['id'];
        $orderId = $paymentData['metadata']['order_id'] ?? null;

        if (!$orderId) {
            return false;
        }

        $order = $this->orderModel->find($orderId);
        if (!$order) {
            return false;
        }

        $this->updateOrderStatus($order, 'payment_failed');
        $this->createPaymentRecord($order, $paymentIntentId, 0, $paymentData['currency'], 'failed');

        return true;
    }

    private function handlePaymentCancellation(array $paymentData): bool
    {
        $orderId = $paymentData['metadata']['order_id'] ?? null;

        if (!$orderId) {
            return false;
        }

        $order = $this->orderModel->find($orderId);
        if ($order) {
            $this->updateOrderStatus($order, 'cancelled');
        }

        return true;
    }

    private function handleUnknownEvent(string $eventType, array $paymentData): bool
    {
        Log::info('Unknown webhook event type received', [
            'event_type' => $eventType,
            'payment_data' => $paymentData
        ]);
        return true;
    }

    private function updateOrderStatus(Order $order, string $status): void
    {
        $order->update(['status' => $status, 'updated_at' => now()]);
    }

    private function createPaymentRecord(Order $order, string $paymentIntentId, float $amount, string $currency, string $status): void
    {
        $this->paymentModel->create([
            'order_id' => $order->id,
            'payment_intent_id' => $paymentIntentId,
            'amount' => $amount,
            'currency' => $currency,
            'status' => $status,
            'processed_at' => now()
        ]);
    }

    private function logWebhookEvent(string $eventId, string $eventType, array $data): void
    {
        $this->webhookLogModel->create([
            'event_id' => $eventId,
            'event_type' => $eventType,
            'payload' => json_encode($data),
            'processed_at' => now()
        ]);
    }
}