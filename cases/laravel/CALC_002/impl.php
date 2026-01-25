<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Order;

class OrderTaxCalculationService
{
    private const TAX_RATE = 0.10;

    private Order $order;
    private float $subtotal;
    private float $discountAmount;

    public function __construct(Order $order)
    {
        $this->order = $order;
        $this->subtotal = $this->calculateSubtotal();
        $this->discountAmount = $this->calculateDiscountAmount();
    }

    public function calculate(): array
    {
        return [
            'subtotal' => $this->subtotal,
            'discount' => $this->discountAmount,
            'tax' => $this->calculateTax(),
            'total' => $this->calculateTotal(),
        ];
    }

    private function calculateSubtotal(): float
    {
        return $this->order->lineItems->sum(function ($item) {
            return $item->quantity * $item->unit_price;
        });
    }

    private function calculateDiscountAmount(): float
    {
        $discountCode = $this->order->discountCode;

        if (!$discountCode) {
            return 0.0;
        }

        return match ($discountCode->discount_type) {
            'percentage' => $this->subtotal * ($discountCode->value / 100.0),
            'fixed' => min($discountCode->value, $this->subtotal),
            default => 0.0,
        };
    }

    private function calculateTax(): float
    {
        return $this->taxableAmount() * self::TAX_RATE;
    }

    private function taxableAmount(): float
    {
        return max($this->subtotal, 0.0);
    }

    private function calculateTotal(): float
    {
        return $this->taxedSubtotal() - $this->discountAmount;
    }

    private function taxedSubtotal(): float
    {
        return $this->subtotal * (1 + self::TAX_RATE);
    }
}
