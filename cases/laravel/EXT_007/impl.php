<?php

namespace App\Services;

use Illuminate\Http\Client\Response;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use App\Models\PaymentTransaction;
use App\Exceptions\PaymentServiceException;

class PaymentGatewayService
{
    public function __construct(
        private readonly string $apiBaseUrl,
        private readonly string $apiKey,
        private readonly int $timeoutSeconds = 30
    ) {}

    public function processPayment(array $paymentData): array
    {
        $response = $this->makePaymentRequest($paymentData);
        
        if (!$response->successful()) {
            throw new PaymentServiceException('Payment gateway request failed');
        }

        return $this->handlePaymentResponse($response, $paymentData);
    }

    public function verifyPaymentStatus(string $transactionId): string
    {
        $response = $this->makeStatusRequest($transactionId);
        
        if (!$response->successful()) {
            Log::error('Payment status verification failed', [
                'transaction_id' => $transactionId,
                'status_code' => $response->status()
            ]);
            throw new PaymentServiceException('Unable to verify payment status');
        }

        $status = $response->json()['status'];
        
        $this->updateTransactionStatus($transactionId, $status);
        
        return $status;
    }

    public function refundPayment(string $transactionId, float $amount): bool
    {
        $refundData = [
            'transaction_id' => $transactionId,
            'amount' => $amount,
            'reason' => 'Customer request'
        ];

        $response = $this->makeRefundRequest($refundData);
        
        if (!$response->successful()) {
            return false;
        }

        $responseData = $response->json();
        $refundStatus = $responseData['refund_status'];
        
        return $refundStatus === 'completed';
    }

    private function makePaymentRequest(array $paymentData): Response
    {
        return Http::withHeaders($this->getAuthHeaders())
            ->timeout($this->timeoutSeconds)
            ->post("{$this->apiBaseUrl}/payments", [
                'amount' => $paymentData['amount'],
                'currency' => $paymentData['currency'],
                'payment_method' => $paymentData['payment_method'],
                'customer_id' => $paymentData['customer_id']
            ]);
    }

    private function makeStatusRequest(string $transactionId): Response
    {
        return Http::withHeaders($this->getAuthHeaders())
            ->timeout($this->timeoutSeconds)
            ->get("{$this->apiBaseUrl}/payments/{$transactionId}/status");
    }

    private function makeRefundRequest(array $refundData): Response
    {
        return Http::withHeaders($this->getAuthHeaders())
            ->timeout($this->timeoutSeconds)
            ->post("{$this->apiBaseUrl}/refunds", $refundData);
    }

    private function handlePaymentResponse(Response $response, array $paymentData): array
    {
        $responseData = $response->json();
        
        $transaction = PaymentTransaction::create([
            'external_id' => $responseData['transaction_id'],
            'amount' => $paymentData['amount'],
            'currency' => $paymentData['currency'],
            'status' => $responseData['status'],
            'gateway_response' => $responseData
        ]);

        return [
            'transaction_id' => $transaction->external_id,
            'status' => $responseData['status'],
            'amount' => $paymentData['amount']
        ];
    }

    private function updateTransactionStatus(string $transactionId, string $status): void
    {
        PaymentTransaction::where('external_id', $transactionId)
            ->update(['status' => $status]);
    }

    private function getAuthHeaders(): array
    {
        return [
            'Authorization' => "Bearer {$this->apiKey}",
            'Content-Type' => 'application/json',
            'Accept' => 'application/json'
        ];
    }
}