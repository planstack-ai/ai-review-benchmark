<?php

namespace App\Services;

use App\Models\Order;
use App\Jobs\ProcessOrderPayment;
use App\Jobs\SendOrderConfirmation;
use App\Jobs\UpdateInventory;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Queue;

class OrderProcessingService
{
    public function __construct(
        private readonly string $queueConnection = 'sync'
    ) {}

    public function processOrder(Order $order): bool
    {
        try {
            DB::beginTransaction();

            $this->validateOrderData($order);
            $this->updateOrderStatus($order, 'processing');

            $this->dispatchOrderJobs($order);

            DB::commit();
            
            Log::info('Order processing initiated', [
                'order_id' => $order->id,
                'customer_id' => $order->customer_id,
                'total' => $order->total_amount
            ]);

            return true;

        } catch (\Exception $e) {
            DB::rollBack();
            
            Log::error('Order processing failed', [
                'order_id' => $order->id,
                'error' => $e->getMessage()
            ]);

            $this->updateOrderStatus($order, 'failed');
            
            return false;
        }
    }

    private function validateOrderData(Order $order): void
    {
        if ($order->status !== 'pending') {
            throw new \InvalidArgumentException('Order must be in pending status');
        }

        if ($order->total_amount <= 0) {
            throw new \InvalidArgumentException('Order total must be greater than zero');
        }

        if (!$order->customer) {
            throw new \InvalidArgumentException('Order must have a valid customer');
        }
    }

    private function updateOrderStatus(Order $order, string $status): void
    {
        $order->update([
            'status' => $status,
            'processed_at' => now()
        ]);
    }

    private function dispatchOrderJobs(Order $order): void
    {
        Queue::connection($this->queueConnection)
            ->push(new ProcessOrderPayment($order));

        Queue::connection($this->queueConnection)
            ->push(new UpdateInventory($order));

        Queue::connection($this->queueConnection)
            ->push(new SendOrderConfirmation($order));
    }

    public function getQueueMetrics(): array
    {
        return [
            'connection' => $this->queueConnection,
            'pending_jobs' => $this->getPendingJobsCount(),
            'failed_jobs' => $this->getFailedJobsCount()
        ];
    }

    private function getPendingJobsCount(): int
    {
        return DB::table('jobs')->count();
    }

    private function getFailedJobsCount(): int
    {
        return DB::table('failed_jobs')->count();
    }

    public function retryFailedOrders(): int
    {
        $failedOrders = Order::where('status', 'failed')
            ->where('created_at', '>=', now()->subHours(24))
            ->get();

        $retryCount = 0;

        foreach ($failedOrders as $order) {
            if ($this->processOrder($order)) {
                $retryCount++;
            }
        }

        return $retryCount;
    }
}