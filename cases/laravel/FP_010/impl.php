<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Order;
use App\Models\Payment;
use App\Models\WebhookEvent;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class PaymentWebhookService
{
    private string $webhookSecret;

    public function __construct()
    {
        $this->webhookSecret = config('payment.webhook_secret');
    }

    public function handleWebhook(Request $request): array
    {
        // Verify signature first
        if (!$this->verifySignature($request)) {
            Log::warning('Webhook signature verification failed', [
                'ip' => $request->ip(),
            ]);

            return [
                'success' => false,
                'message' => 'Invalid signature',
            ];
        }

        $payload = $request->all();
        $eventId = $payload['id'] ?? null;
        $eventType = $payload['type'] ?? null;

        if (!$eventId || !$eventType) {
            return [
                'success' => false,
                'message' => 'Missing required fields',
            ];
        }

        // Idempotency check - return success if already processed
        $existing = WebhookEvent::where('event_id', $eventId)->first();
        if ($existing) {
            Log::info("Webhook event already processed: {$eventId}");

            return [
                'success' => true,
                'message' => 'Event already processed',
            ];
        }

        return DB::transaction(function () use ($eventId, $eventType, $payload) {
            // Create event record for idempotency
            $event = WebhookEvent::create([
                'event_id' => $eventId,
                'event_type' => $eventType,
                'payload' => $payload,
                'status' => 'pending',
            ]);

            try {
                $this->processEvent($eventType, $payload);
                $event->update(['status' => 'processed']);

                return ['success' => true];
            } catch (\Exception $e) {
                $event->update(['status' => 'failed']);
                Log::error("Webhook processing failed: {$e->getMessage()}", [
                    'event_id' => $eventId,
                ]);

                throw $e;
            }
        });
    }

    private function verifySignature(Request $request): bool
    {
        $signature = $request->header('X-Webhook-Signature');
        if (!$signature) {
            return false;
        }

        $payload = $request->getContent();
        $expectedSignature = hash_hmac('sha256', $payload, $this->webhookSecret);

        return hash_equals($expectedSignature, $signature);
    }

    private function processEvent(string $eventType, array $payload): void
    {
        match ($eventType) {
            'payment.completed' => $this->handlePaymentCompleted($payload),
            'payment.failed' => $this->handlePaymentFailed($payload),
            'refund.completed' => $this->handleRefundCompleted($payload),
            default => Log::info("Unhandled webhook event type: {$eventType}"),
        };
    }

    private function handlePaymentCompleted(array $payload): void
    {
        $externalId = $payload['data']['payment_id'];
        $payment = Payment::where('external_id', $externalId)->first();

        if (!$payment) {
            Log::warning("Payment not found for webhook: {$externalId}");

            return;
        }

        $payment->update(['status' => 'completed']);
        $payment->order->update(['status' => 'paid']);
    }

    private function handlePaymentFailed(array $payload): void
    {
        $externalId = $payload['data']['payment_id'];
        $payment = Payment::where('external_id', $externalId)->first();

        if ($payment) {
            $payment->update(['status' => 'failed']);
        }
    }

    private function handleRefundCompleted(array $payload): void
    {
        $externalId = $payload['data']['payment_id'];
        $payment = Payment::where('external_id', $externalId)->first();

        if ($payment) {
            $payment->update(['status' => 'refunded']);
            $payment->order->update(['status' => 'refunded']);
        }
    }
}
