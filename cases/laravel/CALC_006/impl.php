<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Order;

class ShippingCalculatorService
{
    private const STANDARD_SHIPPING_FEE = 500;
    private const EXPRESS_SHIPPING_FEE = 800;
    private const FREE_SHIPPING_THRESHOLD = 5000;

    private Order $order;
    private float $totalAmount;
    private string $shippingMethod;

    public function __construct(Order $order)
    {
        $this->order = $order;
        $this->totalAmount = $this->calculateOrderTotal();
        $this->shippingMethod = $order->shipping_method ?? 'standard';
    }

    public function calculate(): int
    {
        if ($this->freeShippingEligible()) {
            return 0;
        }

        return $this->calculateShippingFee();
    }

    private function freeShippingEligible(): bool
    {
        if (!$this->standardShipping()) {
            return false;
        }

        if ($this->internationalOrder()) {
            return false;
        }

        return $this->totalAmount > self::FREE_SHIPPING_THRESHOLD;
    }

    private function calculateShippingFee(): int
    {
        return match ($this->shippingMethod) {
            'express' => $this->calculateExpressShipping(),
            'standard' => self::STANDARD_SHIPPING_FEE,
            default => self::STANDARD_SHIPPING_FEE,
        };
    }

    private function calculateExpressShipping(): int
    {
        $baseFee = self::EXPRESS_SHIPPING_FEE;

        if ($this->heavyOrder()) {
            $baseFee += $this->additionalWeightFee();
        }

        return $baseFee;
    }

    private function calculateOrderTotal(): float
    {
        $subtotal = $this->order->lineItems->sum('total_price');
        $subtotal += $this->order->tax_amount ?? 0;
        $subtotal -= $this->order->discount_amount ?? 0;

        return $subtotal;
    }

    private function standardShipping(): bool
    {
        return $this->shippingMethod === 'standard';
    }

    private function internationalOrder(): bool
    {
        return $this->order->shippingAddress?->country !== 'JP';
    }

    private function heavyOrder(): bool
    {
        return $this->totalWeight() > 10000;
    }

    private function totalWeight(): int
    {
        return $this->order->lineItems->sum(function ($item) {
            return $item->product->weight * $item->quantity;
        });
    }

    private function additionalWeightFee(): int
    {
        $excessWeight = $this->totalWeight() - 10000;

        return (int) ceil($excessWeight / 1000.0) * 100;
    }
}
