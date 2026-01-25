<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;
use App\Models\Order;
use Carbon\Carbon;

class PointsCalculationService
{
    private const STANDARD_POINT_RATE = 0.01;
    private const PREMIUM_POINT_RATE = 0.02;
    private const MINIMUM_PURCHASE_FOR_POINTS = 10.00;

    private User $user;
    private Order $order;

    public function __construct(User $user, Order $order)
    {
        $this->user = $user;
        $this->order = $order;
    }

    public function calculatePoints(): int
    {
        if (!$this->eligibleForPoints()) {
            return 0;
        }

        $basePoints = $this->calculateBasePoints();
        $bonusPoints = $this->calculateBonusPoints();

        $totalPoints = $basePoints + $bonusPoints;

        return (int) round($this->applyPointMultipliers($totalPoints));
    }

    private function eligibleForPoints(): bool
    {
        if ($this->order->total < self::MINIMUM_PURCHASE_FOR_POINTS) {
            return false;
        }

        if ($this->order->isCancelled()) {
            return false;
        }

        if ($this->user->isPointsSuspended()) {
            return false;
        }

        return true;
    }

    private function calculateBasePoints(): float
    {
        $pointRate = $this->determinePointRate();
        $points = $this->order->subtotal * $pointRate;

        return round($points, 2);
    }

    private function calculateBonusPoints(): int
    {
        $bonus = 0;

        if ($this->firstTimeCustomer()) {
            $bonus += 50;
        }

        if ($this->order->total > 100) {
            $bonus += 25;
        }

        if ($this->seasonalPromotionActive()) {
            $bonus += $this->calculateSeasonalBonus();
        }

        return $bonus;
    }

    private function determinePointRate(): float
    {
        return $this->user->isPremiumMember()
            ? self::PREMIUM_POINT_RATE
            : self::STANDARD_POINT_RATE;
    }

    private function applyPointMultipliers(float $points): float
    {
        $multiplier = 1.0;

        if ($this->user->loyalty_tier === 'gold') {
            $multiplier = 1.5;
        } elseif ($this->user->loyalty_tier === 'silver') {
            $multiplier = 1.2;
        }

        if ($this->weekendBonusActive()) {
            $multiplier *= 1.1;
        }

        return $points * $multiplier;
    }

    private function firstTimeCustomer(): bool
    {
        return $this->user->orders()->completed()->count() === 1;
    }

    private function seasonalPromotionActive(): bool
    {
        $currentMonth = Carbon::now()->month;

        return in_array($currentMonth, [11, 12, 1]);
    }

    private function calculateSeasonalBonus(): int
    {
        return (int) round($this->order->total * 0.005);
    }

    private function weekendBonusActive(): bool
    {
        return Carbon::now()->isWeekend();
    }
}
