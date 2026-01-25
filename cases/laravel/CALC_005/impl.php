<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Order;

class OrderTaxCalculationService
{
    private Order $order;
    private array $taxExemptItems;

    public function __construct(Order $order)
    {
        $this->order = $order;
        $this->taxExemptItems = ['books', 'medical_supplies', 'groceries'];
    }

    public function calculate(): array
    {
        if ($this->orderTaxExempt()) {
            return $this->buildResult(0.0, 0.0);
        }

        $taxableSubtotal = $this->calculateTaxableSubtotal();
        $taxAmount = $this->calculateTaxAmount($taxableSubtotal);

        return $this->buildResult($taxableSubtotal, $taxAmount);
    }

    private function orderTaxExempt(): bool
    {
        return $this->order->customer?->isTaxExempt()
            || strtolower($this->order->shippingAddress?->state ?? '') === 'oregon'
            || $this->allItemsTaxExempt();
    }

    private function allItemsTaxExempt(): bool
    {
        return $this->order->lineItems->every(function ($item) {
            return $this->taxExemptCategory($item->product->category);
        });
    }

    private function taxExemptCategory(?string $category): bool
    {
        return in_array(strtolower($category ?? ''), $this->taxExemptItems);
    }

    private function calculateTaxableSubtotal(): float
    {
        $taxableAmount = 0.0;

        foreach ($this->order->lineItems as $lineItem) {
            if (!$this->taxExemptCategory($lineItem->product->category)) {
                $itemTotal = $lineItem->quantity * $lineItem->unit_price;
                $itemTotal -= $this->applyItemDiscounts($lineItem, $itemTotal);
                $taxableAmount += $itemTotal;
            }
        }

        if ($this->order->discount_amount > 0) {
            $taxableAmount -= $this->order->discount_amount;
        }

        return max($taxableAmount, 0.0);
    }

    private function applyItemDiscounts($lineItem, float $itemTotal): float
    {
        $discount = 0.0;

        if ($lineItem->product->on_sale) {
            $discount += $itemTotal * ($lineItem->product->sale_percentage / 100.0);
        }

        if ($this->bulkDiscountEligible($lineItem)) {
            $discount += $itemTotal * 0.05;
        }

        return $discount;
    }

    private function bulkDiscountEligible($lineItem): bool
    {
        return $lineItem->quantity >= 10 && $lineItem->product->bulk_discount_eligible;
    }

    private function calculateTaxAmount(float $subtotal): float
    {
        if ($subtotal <= 0) {
            return 0.0;
        }

        $baseTax = $subtotal * 0.08;

        if ($this->luxuryTaxApplicable()) {
            $baseTax += $this->calculateLuxuryTax($subtotal);
        }

        return round($baseTax, 2);
    }

    private function luxuryTaxApplicable(): bool
    {
        return $this->order->lineItems->contains(function ($item) {
            return $this->luxuryItem($item->product);
        });
    }

    private function luxuryItem($product): bool
    {
        $luxuryCategories = ['jewelry', 'watches', 'luxury_electronics'];

        return in_array(strtolower($product->category ?? ''), $luxuryCategories)
            || $product->price > 1000;
    }

    private function calculateLuxuryTax(float $subtotal): float
    {
        $luxuryItemsTotal = $this->order->lineItems
            ->filter(fn($item) => $this->luxuryItem($item->product))
            ->sum(fn($item) => $item->quantity * $item->unit_price);

        return $luxuryItemsTotal * 0.02;
    }

    private function buildResult(float $taxableSubtotal, float $taxAmount): array
    {
        return [
            'taxable_subtotal' => $taxableSubtotal,
            'tax_amount' => $taxAmount,
            'total_with_tax' => $taxableSubtotal + $taxAmount,
            'tax_rate_applied' => $taxAmount > 0
                ? round($taxAmount / $taxableSubtotal * 100, 2)
                : 0.0,
        ];
    }
}
