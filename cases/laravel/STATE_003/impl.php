<?php

declare(strict_types=1);

namespace App\Services;

use App\Contracts\PaymentGateway;
use App\Models\Payment;
use Illuminate\Support\Facades\DB;

class PaymentService
{
    public function __construct(
        private PaymentGateway $gateway
    ) {}

    public function processPayment(int $paymentId, array $paymentDetails): array
    {
        return DB::transaction(function () use ($paymentId, $paymentDetails) {
            $payment = Payment::lockForUpdate()->findOrFail($paymentId);

            if ($payment->status !== 'pending') {
                return [
                    'success' => false,
                    'message' => 'Payment is not in pending state',
                ];
            }

            $payment->update(['status' => 'processing']);

            $result = $this->gateway->charge($payment->amount, $paymentDetails);

            if ($result->success) {
                $payment->update([
                    'status' => 'completed',
                    'gateway_reference' => $result->reference,
                ]);

                return [
                    'success' => true,
                    'payment' => $payment,
                ];
            }

            $payment->update([
                'status' => 'failed',
                'failure_reason' => $result->error,
            ]);

            return [
                'success' => false,
                'message' => $result->error,
            ];
        });
    }

    public function refundPayment(int $paymentId): array
    {
        return DB::transaction(function () use ($paymentId) {
            $payment = Payment::lockForUpdate()->findOrFail($paymentId);

            // BUG: Checks for 'completed' but also allows 'refunding' to proceed
            // If already refunding, should not start another refund
            if (!in_array($payment->status, ['completed', 'refunding'])) {
                return [
                    'success' => false,
                    'message' => 'Only completed payments can be refunded',
                ];
            }

            // BUG: Sets to refunding before calling gateway, but if payment is
            // already 'refunding', this creates a duplicate refund attempt
            $payment->update(['status' => 'refunding']);

            $result = $this->gateway->refund($payment->gateway_reference, $payment->amount);

            if ($result->success) {
                $payment->update(['status' => 'refunded']);

                return [
                    'success' => true,
                    'payment' => $payment,
                ];
            }

            // BUG: On failure, reverts to 'completed', losing the refund attempt history
            // Should stay in 'refunding' or go to 'refund_failed'
            $payment->update([
                'status' => 'completed',
                'failure_reason' => $result->error,
            ]);

            return [
                'success' => false,
                'message' => 'Refund failed: ' . $result->error,
            ];
        });
    }

    public function retryPayment(int $paymentId, array $paymentDetails): array
    {
        $payment = Payment::findOrFail($paymentId);

        if ($payment->status !== 'failed') {
            return [
                'success' => false,
                'message' => 'Only failed payments can be retried',
            ];
        }

        $payment->update(['status' => 'pending']);

        return $this->processPayment($paymentId, $paymentDetails);
    }
}
