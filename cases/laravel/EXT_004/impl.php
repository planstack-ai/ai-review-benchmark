<?php

namespace App\Services;

use App\Models\Order;
use App\Models\User;
use App\Exceptions\OrderCreationException;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Str;

class OrderRetryService
{
    public function __construct(
        private readonly int $maxRetries = 3,
        private readonly int $retryDelayMs = 500
    ) {}

    public function createOrderWithRetry(User $user, array $orderData): Order
    {
        $idempotencyKey = $this->generateIdempotencyKey($user, $orderData);
        $attempt = 0;

        while ($attempt < $this->maxRetries) {
            try {
                return $this->attemptOrderCreation($user, $orderData, $idempotencyKey);
            } catch (\Exception $e) {
                $attempt++;
                
                if ($attempt >= $this->maxRetries) {
                    Log::error('Order creation failed after max retries', [
                        'user_id' => $user->id,
                        'idempotency_key' => $idempotencyKey,
                        'error' => $e->getMessage()
                    ]);
                    
                    throw new OrderCreationException(
                        'Failed to create order after ' . $this->maxRetries . ' attempts',
                        previous: $e
                    );
                }

                $this->handleRetryDelay($attempt);
                Log::warning('Order creation attempt failed, retrying', [
                    'attempt' => $attempt,
                    'user_id' => $user->id,
                    'error' => $e->getMessage()
                ]);
            }
        }

        throw new OrderCreationException('Unexpected error in order creation retry logic');
    }

    private function attemptOrderCreation(User $user, array $orderData, string $idempotencyKey): Order
    {
        return DB::transaction(function () use ($user, $orderData, $idempotencyKey) {
            $this->validateOrderData($orderData);
            
            $processedData = $this->prepareOrderData($user, $orderData, $idempotencyKey);
            
            if ($this->shouldSimulateNetworkFailure()) {
                throw new \RuntimeException('Simulated network timeout');
            }

            return Order::create($processedData);
        });
    }

    private function prepareOrderData(User $user, array $orderData, string $idempotencyKey): array
    {
        return [
            'user_id' => $user->id,
            'idempotency_key' => $idempotencyKey,
            'total_amount' => $orderData['total_amount'],
            'currency' => $orderData['currency'] ?? 'USD',
            'items' => json_encode($orderData['items']),
            'shipping_address' => json_encode($orderData['shipping_address']),
            'billing_address' => json_encode($orderData['billing_address'] ?? $orderData['shipping_address']),
            'status' => 'pending',
            'order_number' => $this->generateOrderNumber(),
        ];
    }

    private function validateOrderData(array $orderData): void
    {
        $required = ['total_amount', 'items', 'shipping_address'];
        
        foreach ($required as $field) {
            if (!isset($orderData[$field])) {
                throw new \InvalidArgumentException("Missing required field: {$field}");
            }
        }

        if ($orderData['total_amount'] <= 0) {
            throw new \InvalidArgumentException('Order total must be greater than zero');
        }

        if (empty($orderData['items'])) {
            throw new \InvalidArgumentException('Order must contain at least one item');
        }
    }

    private function generateIdempotencyKey(User $user, array $orderData): string
    {
        $keyData = [
            'user_id' => $user->id,
            'total_amount' => $orderData['total_amount'],
            'items_hash' => md5(json_encode($orderData['items'])),
            'timestamp' => now()->format('Y-m-d H:i')
        ];

        return hash('sha256', json_encode($keyData));
    }

    private function generateOrderNumber(): string
    {
        return 'ORD-' . now()->format('Ymd') . '-' . strtoupper(Str::random(8));
    }

    private function handleRetryDelay(int $attempt): void
    {
        $delay = $this->retryDelayMs * pow(2, $attempt - 1);
        usleep($delay * 1000);
    }

    private function shouldSimulateNetworkFailure(): bool
    {
        return config('app.env') === 'testing' && rand(1, 10) <= 3;
    }
}