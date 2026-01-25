<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;
use App\Models\Coupon;
use App\Models\CouponUsage;
use Carbon\Carbon;

class CouponRedemptionService
{
    private User $user;
    private string $couponCode;
    private float $orderTotal;
    private array $errors = [];

    public function __construct(User $user, string $couponCode, float $orderTotal)
    {
        $this->user = $user;
        $this->couponCode = strtoupper(trim($couponCode));
        $this->orderTotal = $orderTotal;
    }

    public function redeem(): object
    {
        if ($this->orderTotal <= 0) {
            return $this->failureResult('Order total must be positive');
        }

        $coupon = $this->findCoupon();

        if (!$coupon) {
            return $this->failureResult('Invalid coupon code');
        }

        if (!$coupon->active) {
            return $this->failureResult('Coupon is not active');
        }

        if ($this->couponExpired($coupon)) {
            return $this->failureResult('Coupon has expired');
        }

        if ($this->usageLimitExceeded($coupon)) {
            return $this->failureResult('Coupon usage limit exceeded');
        }

        if (!$this->meetsMinimumAmount($coupon)) {
            return $this->failureResult('Order does not meet minimum amount');
        }

        $discountAmount = $this->calculateDiscount($coupon);

        if ($discountAmount <= 0) {
            return $this->failureResult('Discount cannot be applied');
        }

        $this->createCouponUsage($coupon, $discountAmount);

        return $this->successResult($coupon, $discountAmount);
    }

    private function findCoupon(): ?Coupon
    {
        return Coupon::where('code', $this->couponCode)->first();
    }

    private function couponExpired(Coupon $coupon): bool
    {
        if (!$coupon->expires_at) {
            return false;
        }

        return $coupon->expires_at->isPast();
    }

    private function usageLimitExceeded(Coupon $coupon): bool
    {
        if (!$coupon->usage_limit) {
            return false;
        }

        return $coupon->usages()->count() >= $coupon->usage_limit;
    }

    private function meetsMinimumAmount(Coupon $coupon): bool
    {
        if (!$coupon->minimum_order_amount) {
            return true;
        }

        return $this->orderTotal >= $coupon->minimum_order_amount;
    }

    private function calculateDiscount(Coupon $coupon): float
    {
        $discount = match ($coupon->discount_type) {
            'percentage' => $this->orderTotal * ($coupon->discount_value / 100.0),
            'fixed_amount' => min($coupon->discount_value, $this->orderTotal),
            default => 0.0,
        };

        if ($coupon->discount_type === 'percentage' && $coupon->max_discount_amount) {
            $discount = min($discount, $coupon->max_discount_amount);
        }

        return round($discount, 2);
    }

    private function createCouponUsage(Coupon $coupon, float $discountAmount): void
    {
        CouponUsage::create([
            'coupon_id' => $coupon->id,
            'user_id' => $this->user->id,
            'discount_amount' => $discountAmount,
            'order_total' => $this->orderTotal,
            'used_at' => Carbon::now(),
        ]);
    }

    private function successResult(Coupon $coupon, float $discountAmount): object
    {
        return (object) [
            'success' => true,
            'coupon' => $coupon,
            'discount_amount' => $discountAmount,
            'final_total' => $this->orderTotal - $discountAmount,
            'message' => 'Coupon applied successfully',
        ];
    }

    private function failureResult(string $message): object
    {
        $this->errors[] = $message;

        return (object) [
            'success' => false,
            'coupon' => null,
            'discount_amount' => 0,
            'final_total' => $this->orderTotal,
            'message' => $message,
            'errors' => $this->errors,
        ];
    }
}
