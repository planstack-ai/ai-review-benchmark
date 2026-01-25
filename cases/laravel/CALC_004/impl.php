<?php

declare(strict_types=1);

namespace App\Services;

class PriceCalculationService
{
    private const TAX_RATE = 0.08;
    private const DISCOUNT_THRESHOLD = 100.0;
    private const BULK_DISCOUNT_RATE = 0.05;

    private float $basePrice;
    private int $quantity;
    private ?string $discountCode;

    public function __construct(float $basePrice, int $quantity = 1, ?string $discountCode = null)
    {
        $this->basePrice = $basePrice;
        $this->quantity = $quantity;
        $this->discountCode = $discountCode;
    }

    public function calculateTotal(): float
    {
        $subtotal = $this->calculateSubtotal();
        $discountedAmount = $this->applyDiscounts($subtotal);
        $finalAmount = $this->applyTax($discountedAmount);

        return $this->roundToCurrency($finalAmount);
    }

    public function calculateBreakdown(): array
    {
        $subtotal = $this->calculateSubtotal();
        $discountAmount = $this->calculateDiscountAmount($subtotal);
        $discountedSubtotal = $subtotal - $discountAmount;
        $taxAmount = $this->calculateTaxAmount($discountedSubtotal);
        $total = $discountedSubtotal + $taxAmount;

        return [
            'subtotal' => $this->roundToCurrency($subtotal),
            'discount' => $this->roundToCurrency($discountAmount),
            'tax' => $this->roundToCurrency($taxAmount),
            'total' => $this->roundToCurrency($total),
        ];
    }

    private function calculateSubtotal(): float
    {
        return $this->basePrice * $this->quantity;
    }

    private function applyDiscounts(float $amount): float
    {
        $discountAmount = $this->calculateDiscountAmount($amount);

        return $amount - $discountAmount;
    }

    private function calculateDiscountAmount(float $amount): float
    {
        $totalDiscount = 0.0;

        if ($this->eligibleForBulkDiscount($amount)) {
            $totalDiscount += $amount * self::BULK_DISCOUNT_RATE;
        }

        if ($this->validDiscountCode()) {
            $codeDiscount = $this->calculateCodeDiscount($amount);
            $totalDiscount += $codeDiscount;
        }

        return $totalDiscount;
    }

    private function eligibleForBulkDiscount(float $amount): bool
    {
        return $amount >= self::DISCOUNT_THRESHOLD;
    }

    private function validDiscountCode(): bool
    {
        if (!$this->discountCode) {
            return false;
        }

        $validCodes = ['SAVE10', 'WELCOME5', 'STUDENT15'];

        return in_array(strtoupper($this->discountCode), $validCodes);
    }

    private function calculateCodeDiscount(float $amount): float
    {
        return match (strtoupper($this->discountCode)) {
            'SAVE10' => $amount * 0.1,
            'WELCOME5' => $amount * 0.05,
            'STUDENT15' => $amount * 0.15,
            default => 0.0,
        };
    }

    private function applyTax(float $amount): float
    {
        $taxAmount = $this->calculateTaxAmount($amount);

        return $amount + $taxAmount;
    }

    private function calculateTaxAmount(float $amount): float
    {
        return $amount * self::TAX_RATE;
    }

    private function roundToCurrency(float $amount): float
    {
        return round($amount * 100) / 100.0;
    }
}
