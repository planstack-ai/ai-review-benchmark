<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Order;
use App\Models\Coupon;
use App\Models\CouponUsage;
use Carbon\Carbon;

class CouponApplicationService
{
    private ?Order $order;
    private ?Coupon $coupon;
    private array $errors = [];

    public function __construct(?Order $order, ?Coupon $coupon)
    {
        $this->order = $order;
        $this->coupon = $coupon;
    }

    public function apply(): object
    {
        if (!$this->order) {
            return $this->failure('Order not found');
        }

        if (!$this->coupon) {
            return $this->failure('Coupon not found');
        }

        if (!$this->couponActive()) {
            return $this->failure('Coupon is not active');
        }

        if ($this->couponExpired()) {
            return $this->failure('Coupon has expired');
        }

        if (!$this->meetsMinimumRequirements()) {
            return $this->failure('Order does not meet minimum requirements');
        }

        if ($this->usageLimitExceeded()) {
            return $this->failure('Coupon usage limit exceeded');
        }

        $this->applyCouponDiscount();
        $this->updateOrderTotals();
        $this->recordCouponUsage();

        return $this->success();
    }

    public function isSuccess(): bool
    {
        return empty($this->errors);
    }

    private function couponActive(): bool
    {
        return $this->coupon->isActive();
    }

    private function couponExpired(): bool
    {
        return $this->coupon->isExpired();
    }

    private function meetsMinimumRequirements(): bool
    {
        if (!$this->coupon->minimum_order_amount) {
            return true;
        }

        return $this->order->subtotal >= $this->coupon->minimum_order_amount;
    }

    private function usageLimitExceeded(): bool
    {
        if (!$this->coupon->usage_limit) {
            return false;
        }

        return $this->coupon->usage_count >= $this->coupon->usage_limit;
    }

    private function applyCouponDiscount(): void
    {
        $discountAmount = $this->calculateDiscountAmount();

        $this->order->coupon_discount = $discountAmount;
        $this->order->appliedCoupons()->attach($this->coupon->id);
        $this->order->save();
    }

    private function calculateDiscountAmount(): float
    {
        return match ($this->coupon->discount_type) {
            'percentage' => round($this->order->subtotal * $this->coupon->discount_value / 100.0, 2),
            'fixed_amount' => min($this->coupon->discount_value, $this->order->subtotal),
            default => 0.0,
        };
    }

    private function updateOrderTotals(): void
    {
        $this->order->total = $this->order->subtotal
            - $this->order->coupon_discount
            + $this->order->tax_amount
            + $this->order->shipping_amount;
        $this->order->save();
    }

    private function recordCouponUsage(): void
    {
        $this->coupon->increment('usage_count');

        CouponUsage::create([
            'coupon_id' => $this->coupon->id,
            'order_id' => $this->order->id,
            'discount_amount' => $this->order->coupon_discount,
            'used_at' => Carbon::now(),
        ]);
    }

    private function success(): object
    {
        return (object) ['success' => true, 'errors' => []];
    }

    private function failure(string $message): object
    {
        $this->errors[] = $message;

        return (object) ['success' => false, 'errors' => $this->errors];
    }
}
