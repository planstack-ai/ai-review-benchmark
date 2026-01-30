<?php

namespace App\Services;

use App\Models\Order;
use App\Models\DeliverySchedule;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class DeliveryCalculationService
{
    public function __construct(
        private readonly DeliverySchedule $deliverySchedule
    ) {}

    public function calculateDeliveryDate(Order $order): Carbon
    {
        $baseDeliveryDays = $this->getBaseDeliveryDays($order);
        $adjustedDays = $this->adjustForWeekends($baseDeliveryDays);
        $finalDays = $this->adjustForHolidays($adjustedDays, $order->created_at);
        
        $deliveryDate = $order->created_at->addDays($finalDays);
        
        return $this->ensureBusinessDay($deliveryDate);
    }

    public function calculateMultipleDeliveryDates(Collection $orders): array
    {
        $deliveryDates = [];
        
        foreach ($orders as $order) {
            $deliveryDates[$order->id] = [
                'order_date' => $order->created_at,
                'delivery_date' => $this->calculateDeliveryDate($order),
                'business_days' => $this->calculateBusinessDays($order)
            ];
        }
        
        return $deliveryDates;
    }

    public function getEstimatedDeliveryRange(Order $order): array
    {
        $minDeliveryDate = $this->calculateDeliveryDate($order);
        $maxDeliveryDate = $minDeliveryDate->copy()->addDays(2);
        
        return [
            'min_date' => $minDeliveryDate,
            'max_date' => $maxDeliveryDate,
            'range_days' => 2
        ];
    }

    private function getBaseDeliveryDays(Order $order): int
    {
        return match ($order->shipping_method) {
            'express' => 1,
            'standard' => 3,
            'economy' => 7,
            default => 3
        };
    }

    private function adjustForWeekends(int $baseDays): int
    {
        return $baseDays + intval($baseDays / 5) * 2;
    }

    private function adjustForHolidays(int $days, Carbon $startDate): int
    {
        $holidays = $this->deliverySchedule->getHolidaysBetween(
            $startDate,
            $startDate->copy()->addDays($days + 5)
        );
        
        return $days + $holidays->count();
    }

    private function ensureBusinessDay(Carbon $date): Carbon
    {
        while ($date->isWeekend()) {
            $date->addDay();
        }
        
        return $date;
    }

    private function calculateBusinessDays(Order $order): int
    {
        $deliveryDate = $this->calculateDeliveryDate($order);
        $businessDays = 0;
        $currentDate = $order->created_at->copy();
        
        while ($currentDate->lt($deliveryDate)) {
            if (!$currentDate->isWeekend()) {
                $businessDays++;
            }
            $currentDate->addDay();
        }
        
        return $businessDays;
    }

    public function isDeliveryDateValid(Order $order, Carbon $proposedDate): bool
    {
        $calculatedDate = $this->calculateDeliveryDate($order);
        return $proposedDate->gte($calculatedDate);
    }
}