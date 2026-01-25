<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Order;
use Illuminate\Support\Facades\Validator;

class OrderTotalCalculatorService
{
    private Order $order;
    private float $taxRate;
    private float $discountAmount;

    public function __construct(Order $order, float $taxRate = 0.0, float $discountAmount = 0.0)
    {
        $this->order = $order;
        $this->taxRate = $taxRate;
        $this->discountAmount = $discountAmount;
    }

    public function calculate(): array
    {
        if (!$this->validate()) {
            return $this->failureResult('Invalid parameters');
        }

        if ($this->order->orderItems->isEmpty()) {
            return $this->failureResult('Order has no items');
        }

        try {
            $total = $this->calculateTotal();

            return [
                'success' => true,
                'subtotal' => $this->calculateSubtotal(),
                'tax_amount' => $this->calculateTaxAmount(),
                'discount_amount' => $this->discountAmount,
                'total' => $total,
                'currency' => $this->order->currency ?? 'USD',
            ];
        } catch (\Exception $e) {
            return $this->failureResult("Calculation error: {$e->getMessage()}");
        }
    }

    private function validate(): bool
    {
        return $this->taxRate >= 0 && $this->discountAmount >= 0;
    }

    private function calculateTotal(): float
    {
        $subtotalWithTax = $this->calculateSubtotal() + $this->calculateTaxAmount();
        $finalTotal = $subtotalWithTax - $this->discountAmount;

        return max($finalTotal, 0.0);
    }

    private function calculateSubtotal(): float
    {
        return $this->order->orderItems->sum(function ($item) {
            return round($this->calculateItemSubtotal($item), 2);
        });
    }

    private function calculateItemSubtotal($item): float
    {
        $basePrice = $item->unit_price * $item->quantity;
        $itemDiscount = $this->calculateItemDiscount($item);

        return $basePrice - $itemDiscount;
    }

    private function calculateItemDiscount($item): float
    {
        if (!$item->discount_percentage || $item->discount_percentage <= 0) {
            return 0.0;
        }

        $discountRate = $item->discount_percentage / 100.0;
        $baseAmount = $item->unit_price * $item->quantity;

        return $baseAmount * $discountRate;
    }

    private function calculateTaxAmount(): float
    {
        if ($this->taxRate === 0.0) {
            return 0.0;
        }

        $taxableSubtotal = $this->calculateSubtotal();

        return round($taxableSubtotal * $this->taxRate, 2);
    }

    private function failureResult(string $message): array
    {
        return [
            'success' => false,
            'error' => $message,
            'subtotal' => 0.0,
            'tax_amount' => 0.0,
            'discount_amount' => 0.0,
            'total' => 0.0,
        ];
    }
}
