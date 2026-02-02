<?php

namespace App\Services;

use App\Models\Order;
use App\Models\Payment;
use App\Enums\OrderStatus;
use App\Enums\PaymentStatus;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Str;

class PaymentProcessingService
{
    public function __construct(
        private readonly string $paymentGatewayUrl,
        private readonly string $merchantId,
        private readonly string $apiKey
    ) {}

    public function processPayment(Order $order, array $paymentData): Payment
    {
        $payment = $this->createPaymentRecord($order, $paymentData);
        
        try {
            $response = $this->sendPaymentRequest($payment, $paymentData);
            
            if ($response->successful()) {
                return $this->handleSuccessfulPayment($payment, $response->json());
            }
            
            return $this->handleFailedPayment($payment, $response->json());
            
        } catch (\Exception $e) {
            Log::error('Payment processing failed', [
                'payment_id' => $payment->id,
                'error' => $e->getMessage()
            ]);
            
            $payment->update([
                'status' => PaymentStatus::FAILED,
                'error_message' => 'Payment processing error occurred'
            ]);
            
            throw $e;
        }
    }

    private function createPaymentRecord(Order $order, array $paymentData): Payment
    {
        return Payment::create([
            'order_id' => $order->id,
            'amount' => $order->total_amount,
            'currency' => $order->currency,
            'payment_method' => $paymentData['payment_method'],
            'status' => PaymentStatus::PENDING,
            'transaction_id' => Str::uuid(),
        ]);
    }

    private function sendPaymentRequest(Payment $payment, array $paymentData): \Illuminate\Http\Client\Response
    {
        $payload = $this->buildPaymentPayload($payment, $paymentData);
        
        return Http::withHeaders([
            'Authorization' => 'Bearer ' . $this->apiKey,
            'Content-Type' => 'application/json',
            'X-Merchant-ID' => $this->merchantId,
        ])->post($this->paymentGatewayUrl . '/process', $payload);
    }

    private function buildPaymentPayload(Payment $payment, array $paymentData): array
    {
        return [
            'transaction_id' => $payment->transaction_id,
            'amount' => $payment->amount,
            'currency' => $payment->currency,
            'payment_method' => $paymentData['payment_method'],
            'card_number' => $paymentData['card_number'] ?? null,
            'expiry_month' => $paymentData['expiry_month'] ?? null,
            'expiry_year' => $paymentData['expiry_year'] ?? null,
            'cvv' => $paymentData['cvv'] ?? null,
            'callback_url' => route('payment.callback', $payment->id),
        ];
    }

    private function handleSuccessfulPayment(Payment $payment, array $responseData): Payment
    {
        $payment->update([
            'status' => PaymentStatus::COMPLETED,
            'gateway_transaction_id' => $responseData['gateway_transaction_id'],
            'processed_at' => now(),
        ]);

        $payment->order->update([
            'status' => OrderStatus::PAID,
            'paid_at' => now(),
        ]);

        Log::info('Payment processed successfully', [
            'payment_id' => $payment->id,
            'gateway_transaction_id' => $responseData['gateway_transaction_id'],
        ]);

        return $payment;
    }

    private function handleFailedPayment(Payment $payment, array $responseData): Payment
    {
        $payment->update([
            'status' => PaymentStatus::FAILED,
            'error_message' => $responseData['error_message'] ?? 'Payment failed',
            'gateway_error_code' => $responseData['error_code'] ?? null,
        ]);

        $payment->order->update([
            'status' => OrderStatus::PAYMENT_FAILED,
        ]);

        return $payment;
    }

    public function verifyPaymentStatus(Payment $payment): bool
    {
        $response = Http::withHeaders([
            'Authorization' => 'Bearer ' . $this->apiKey,
            'X-Merchant-ID' => $this->merchantId,
        ])->get($this->paymentGatewayUrl . '/verify/' . $payment->gateway_transaction_id);

        if ($response->successful()) {
            $data = $response->json();
            
            if ($data['status'] === 'completed' && $payment->status !== PaymentStatus::COMPLETED) {
                $this->handleSuccessfulPayment($payment, $data);
                return true;
            }
        }

        return false;
    }
}