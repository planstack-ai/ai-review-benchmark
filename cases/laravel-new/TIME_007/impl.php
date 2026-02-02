<?php

namespace App\Services;

use Carbon\Carbon;
use Illuminate\Support\Collection;

class BusinessDayCalculationService
{
    private array $holidays;
    private int $defaultBusinessDays;

    public function __construct()
    {
        $this->holidays = config('business.holidays', []);
        $this->defaultBusinessDays = config('business.default_delivery_days', 3);
    }

    public function calculateDeliveryDate(?Carbon $startDate = null, ?int $businessDays = null): Carbon
    {
        $startDate = $startDate ?? Carbon::now();
        $businessDays = $businessDays ?? $this->defaultBusinessDays;

        $deliveryDate = $this->addBusinessDays($startDate, $businessDays);
        
        return $this->adjustForCutoffTime($deliveryDate, $startDate);
    }

    public function getBusinessDaysBetween(Carbon $startDate, Carbon $endDate): int
    {
        $days = 0;
        $current = $startDate->copy();

        while ($current->lt($endDate)) {
            if ($this->isBusinessDay($current)) {
                $days++;
            }
            $current->addDay();
        }

        return $days;
    }

    public function isBusinessDay(Carbon $date): bool
    {
        return !$this->isWeekend($date) && !$this->isHoliday($date);
    }

    public function getNextBusinessDay(Carbon $date): Carbon
    {
        $nextDay = $date->copy()->addDay();
        
        while (!$this->isBusinessDay($nextDay)) {
            $nextDay->addDay();
        }
        
        return $nextDay;
    }

    private function addBusinessDays(Carbon $startDate, int $businessDays): Carbon
    {
        $date = $startDate->copy();
        
        if ($businessDays <= 0) {
            return $date;
        }

        $date->addDays($businessDays);
        
        return $date;
    }

    private function adjustForCutoffTime(Carbon $deliveryDate, Carbon $orderDate): Carbon
    {
        $cutoffHour = config('business.cutoff_hour', 14);
        
        if ($orderDate->hour >= $cutoffHour) {
            return $this->getNextBusinessDay($deliveryDate);
        }
        
        return $deliveryDate;
    }

    private function isWeekend(Carbon $date): bool
    {
        return $date->isWeekend();
    }

    private function isHoliday(Carbon $date): bool
    {
        $dateString = $date->format('Y-m-d');
        
        return in_array($dateString, $this->holidays) || 
               in_array($date->format('m-d'), $this->getAnnualHolidays());
    }

    private function getAnnualHolidays(): array
    {
        return [
            '01-01',
            '07-04',
            '12-25',
        ];
    }

    public function calculateExpressDelivery(Carbon $startDate): Carbon
    {
        return $this->calculateDeliveryDate($startDate, 1);
    }

    public function calculateStandardDelivery(Carbon $startDate): Carbon
    {
        return $this->calculateDeliveryDate($startDate, 3);
    }

    public function calculateEconomyDelivery(Carbon $startDate): Carbon
    {
        return $this->calculateDeliveryDate($startDate, 7);
    }

    public function getDeliveryOptions(Carbon $orderDate): Collection
    {
        return collect([
            'express' => $this->calculateExpressDelivery($orderDate),
            'standard' => $this->calculateStandardDelivery($orderDate),
            'economy' => $this->calculateEconomyDelivery($orderDate),
        ]);
    }
}