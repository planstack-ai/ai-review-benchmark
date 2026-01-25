<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Subscription;
use Illuminate\Support\Carbon;

class BillingService
{
    public function calculateNextBillingDate(Subscription $subscription): Carbon
    {
        $currentPeriodEnd = Carbon::parse($subscription->current_period_end);
        $billingDay = $subscription->billing_day;

        // BUG: Simply adds one month without handling month-end cases
        // If billing_day is 31 and next month has 30 days, this will overflow
        $nextBilling = $currentPeriodEnd->copy()->addMonth();
        $nextBilling->day = $billingDay;

        return $nextBilling;
    }

    public function calculateProration(Subscription $subscription, float $newPrice): array
    {
        $periodStart = Carbon::parse($subscription->current_period_start);
        $periodEnd = Carbon::parse($subscription->current_period_end);
        $today = now();

        // BUG: Uses diffInDays which can have off-by-one depending on time
        // Should use startOfDay() for consistent day counting
        $totalDays = $periodStart->diffInDays($periodEnd);
        $remainingDays = $today->diffInDays($periodEnd);

        $currentPrice = $subscription->plan->monthly_price;

        // Credit for unused time on old plan
        $credit = ($remainingDays / $totalDays) * $currentPrice;

        // Charge for remaining time on new plan
        $charge = ($remainingDays / $totalDays) * $newPrice;

        return [
            'credit' => round($credit, 2),
            'charge' => round($charge, 2),
            'net' => round($charge - $credit, 2),
            'remaining_days' => $remainingDays,
            'total_days' => $totalDays,
        ];
    }

    public function renewSubscription(Subscription $subscription): array
    {
        $nextBillingDate = $this->calculateNextBillingDate($subscription);

        $subscription->update([
            'current_period_start' => $subscription->current_period_end,
            'current_period_end' => $nextBillingDate,
        ]);

        return [
            'success' => true,
            'next_billing_date' => $nextBillingDate,
        ];
    }

    public function getMonthlyBillingDate(int $billingDay, Carbon $forMonth): Carbon
    {
        $date = $forMonth->copy()->startOfMonth();
        $lastDayOfMonth = $date->daysInMonth;

        // BUG: This logic is here but calculateNextBillingDate doesn't use it
        if ($billingDay > $lastDayOfMonth) {
            $date->day = $lastDayOfMonth;
        } else {
            $date->day = $billingDay;
        }

        return $date;
    }
}
