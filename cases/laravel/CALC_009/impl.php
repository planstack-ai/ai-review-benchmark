<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Order;

class OrderValidationService
{
    private const MINIMUM_ORDER_AMOUNT = 1000;

    private Order $order;
    private array $errors = [];

    public function __construct(Order $order)
    {
        $this->order = $order;
    }

    public function isValid(): bool
    {
        $this->errors = [];

        $this->validateMinimumAmount();
        $this->validateOrderItems();
        $this->validateCustomerEligibility();

        return empty($this->errors);
    }

    public function getErrors(): array
    {
        return $this->errors;
    }

    public function validationSummary(): array
    {
        return [
            'valid' => $this->isValid(),
            'errors' => $this->getErrors(),
            'order_total' => $this->calculateOrderTotal(),
            'discount_amount' => $this->calculateTotalDiscount(),
        ];
    }

    private function validateMinimumAmount(): void
    {
        $subtotal = $this->calculateSubtotal();

        if ($subtotal < self::MINIMUM_ORDER_AMOUNT) {
            $this->errors[] = 'Order must be at least ' . self::MINIMUM_ORDER_AMOUNT . ' yen';
        }
    }

    private function validateOrderItems(): void
    {
        if ($this->order->orderItems->isEmpty()) {
            $this->errors[] = 'Order must contain at least one item';
        }

        foreach ($this->order->orderItems as $item) {
            if ($item->quantity <= 0) {
                $this->errors[] = 'Item quantity must be greater than zero';
            }

            if ($item->unit_price < 0) {
                $this->errors[] = 'Item price cannot be negative';
            }
        }
    }

    private function validateCustomerEligibility(): void
    {
        if (!$this->order->customer) {
            return;
        }

        if ($this->order->customer->isBlocked()) {
            $this->errors[] = 'Customer account is blocked';
        }

        if ($this->order->customer->hasPaymentOverdue()) {
            $this->errors[] = 'Customer has overdue payments';
        }
    }

    private function calculateSubtotal(): float
    {
        return $this->order->orderItems->sum(function ($item) {
            return $item->quantity * $item->unit_price;
        });
    }

    private function calculateTotalDiscount(): float
    {
        $baseDiscount = $this->calculatePercentageDiscount();
        $couponDiscount = $this->calculateCouponDiscount();
        $loyaltyDiscount = $this->calculateLoyaltyDiscount();

        $totalDiscount = $baseDiscount + $couponDiscount + $loyaltyDiscount;

        return min($totalDiscount, $this->calculateSubtotal() * 0.5);
    }

    private function calculatePercentageDiscount(): float
    {
        $subtotal = $this->calculateSubtotal();

        if (!$this->order->discount_percentage) {
            return 0;
        }

        return round($subtotal * $this->order->discount_percentage / 100.0);
    }

    private function calculateCouponDiscount(): float
    {
        if (!$this->order->coupon?->isActive()) {
            return 0;
        }

        return min($this->order->coupon->discount_amount, $this->calculateSubtotal());
    }

    private function calculateLoyaltyDiscount(): float
    {
        if (!$this->order->customer?->isLoyaltyMember()) {
            return 0;
        }

        return round($this->calculateSubtotal() * 0.05);
    }

    private function calculateOrderTotal(): float
    {
        return $this->calculateSubtotal() - $this->calculateTotalDiscount();
    }
}
