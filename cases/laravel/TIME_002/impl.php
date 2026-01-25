<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Coupon;
use Illuminate\Support\Carbon;

class CouponService
{
    public function validateCoupon(string $code): array
    {
        $coupon = Coupon::where('code', strtoupper($code))->first();

        if (!$coupon) {
            return [
                'valid' => false,
                'message' => 'Coupon not found',
            ];
        }

        if (!$coupon->active) {
            return [
                'valid' => false,
                'message' => 'Coupon is not active',
            ];
        }

        // BUG: Uses now() which includes time, comparing to date columns
        // On the end date, now() could be 2024-01-31 15:00:00
        // valid_until is 2024-01-31 (stored as 2024-01-31 00:00:00)
        // Comparison: 2024-01-31 15:00:00 > 2024-01-31 00:00:00 = EXPIRED!
        $today = now();

        if ($today->lt($coupon->valid_from)) {
            return [
                'valid' => false,
                'message' => 'Coupon is not yet valid',
            ];
        }

        if ($today->gt($coupon->valid_until)) {
            return [
                'valid' => false,
                'message' => 'Coupon has expired',
            ];
        }

        if ($coupon->usage_limit && $coupon->used_count >= $coupon->usage_limit) {
            return [
                'valid' => false,
                'message' => 'Coupon usage limit reached',
            ];
        }

        return [
            'valid' => true,
            'coupon' => $coupon,
        ];
    }

    public function applyCoupon(string $code, float $orderTotal): array
    {
        $validation = $this->validateCoupon($code);

        if (!$validation['valid']) {
            return $validation;
        }

        $coupon = $validation['coupon'];
        $discount = $this->calculateDiscount($coupon, $orderTotal);

        return [
            'valid' => true,
            'discount' => $discount,
            'final_total' => $orderTotal - $discount,
        ];
    }

    public function redeemCoupon(string $code): array
    {
        $coupon = Coupon::where('code', strtoupper($code))->first();

        if (!$coupon) {
            return ['success' => false, 'message' => 'Coupon not found'];
        }

        $coupon->increment('used_count');

        return ['success' => true];
    }

    private function calculateDiscount(Coupon $coupon, float $orderTotal): float
    {
        if ($coupon->discount_amount) {
            return min($coupon->discount_amount, $orderTotal);
        }

        if ($coupon->discount_percent) {
            return $orderTotal * ($coupon->discount_percent / 100);
        }

        return 0;
    }
}
