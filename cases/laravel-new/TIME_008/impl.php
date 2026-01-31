<?php

namespace App\Services;

use App\Models\Delivery;
use App\Models\Order;
use Carbon\Carbon;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\ValidationException;

class DeliverySchedulingService
{
    public function __construct(
        private readonly Delivery $deliveryModel,
        private readonly Order $orderModel
    ) {}

    public function scheduleDelivery(int $orderId, array $deliveryData): Delivery
    {
        $order = $this->orderModel->findOrFail($orderId);
        
        $this->validateDeliveryData($deliveryData);
        
        $processedData = $this->processDeliveryData($deliveryData, $order);
        
        return $this->createDeliveryRecord($order, $processedData);
    }

    public function updateDeliverySchedule(int $deliveryId, array $deliveryData): Delivery
    {
        $delivery = $this->deliveryModel->findOrFail($deliveryId);
        
        $this->validateDeliveryData($deliveryData);
        
        $processedData = $this->processDeliveryData($deliveryData, $delivery->order);
        
        $delivery->update($processedData);
        
        return $delivery->fresh();
    }

    public function getAvailableDeliverySlots(Carbon $startDate, Carbon $endDate): array
    {
        $existingDeliveries = $this->deliveryModel
            ->whereBetween('delivery_date', [$startDate, $endDate])
            ->pluck('delivery_date')
            ->toArray();

        $availableSlots = [];
        $currentDate = $startDate->copy();

        while ($currentDate->lte($endDate)) {
            if (!in_array($currentDate->format('Y-m-d'), $existingDeliveries)) {
                $availableSlots[] = $currentDate->format('Y-m-d');
            }
            $currentDate->addDay();
        }

        return $availableSlots;
    }

    private function validateDeliveryData(array $data): void
    {
        $validator = Validator::make($data, [
            'delivery_date' => 'required|date',
            'delivery_time' => 'required|string|in:morning,afternoon,evening',
            'special_instructions' => 'nullable|string|max:500',
            'delivery_address' => 'required|string|max:255',
            'contact_phone' => 'required|string|regex:/^[0-9\-\+\(\)\s]+$/',
        ]);

        if ($validator->fails()) {
            throw new ValidationException($validator);
        }
    }

    private function processDeliveryData(array $data, Order $order): array
    {
        $deliveryDate = Carbon::parse($data['delivery_date']);
        
        $estimatedDuration = $this->calculateDeliveryDuration($order);
        
        return [
            'delivery_date' => $deliveryDate->format('Y-m-d'),
            'delivery_time' => $data['delivery_time'],
            'estimated_duration' => $estimatedDuration,
            'special_instructions' => $data['special_instructions'] ?? null,
            'delivery_address' => $data['delivery_address'],
            'contact_phone' => $data['contact_phone'],
            'status' => 'scheduled',
            'scheduled_at' => now(),
        ];
    }

    private function createDeliveryRecord(Order $order, array $deliveryData): Delivery
    {
        return $order->delivery()->create($deliveryData);
    }

    private function calculateDeliveryDuration(Order $order): int
    {
        $baseTime = 30;
        $itemCount = $order->items()->count();
        
        return $baseTime + ($itemCount * 5);
    }

    public function cancelDelivery(int $deliveryId, string $reason): bool
    {
        $delivery = $this->deliveryModel->findOrFail($deliveryId);
        
        return $delivery->update([
            'status' => 'cancelled',
            'cancellation_reason' => $reason,
            'cancelled_at' => now(),
        ]);
    }
}