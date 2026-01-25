<?php

declare(strict_types=1);

namespace App\Services;

use InvalidArgumentException;

class BulkOrderCalculationService
{
    private array $orderItems;
    private float $discountPercentage;
    private float $taxRate;

    public function __construct(array $orderItems, float $discountPercentage = 0, float $taxRate = 0.08)
    {
        $this->orderItems = $orderItems;
        $this->discountPercentage = $discountPercentage;
        $this->taxRate = $taxRate;
    }

    public function calculateTotal(): ServiceResult
    {
        if (!$this->validate()) {
            return new ServiceResult(false, null, ['Invalid parameters']);
        }

        $subtotal = $this->calculateSubtotal();
        $discountAmount = $this->calculateDiscount($subtotal);
        $discountedSubtotal = $subtotal - $discountAmount;
        $taxAmount = $this->calculateTax($discountedSubtotal);
        $finalTotal = $discountedSubtotal + $taxAmount;

        return new ServiceResult(true, [
            'subtotal' => $this->formatCurrency($subtotal),
            'discount_amount' => $this->formatCurrency($discountAmount),
            'tax_amount' => $this->formatCurrency($taxAmount),
            'total' => $this->formatCurrency($finalTotal),
            'item_count' => $this->totalItemCount(),
        ]);
    }

    public function bulkDiscountEligible(): bool
    {
        return $this->totalItemCount() >= 100 || $this->calculateSubtotal() >= 10000;
    }

    private function validate(): bool
    {
        if (empty($this->orderItems)) {
            return false;
        }

        if ($this->discountPercentage < 0 || $this->discountPercentage > 100) {
            return false;
        }

        return true;
    }

    private function calculateSubtotal(): float
    {
        $total = 0.0;

        foreach ($this->orderItems as $item) {
            $unitPrice = $item['unit_price'] ?? $item->unit_price ?? 0;
            $quantity = $item['quantity'] ?? $item->quantity ?? 0;

            $this->validateItemData($unitPrice, $quantity);

            $total += $unitPrice * $quantity;
        }

        return $total;
    }

    private function calculateDiscount(float $subtotal): float
    {
        if ($this->discountPercentage === 0.0) {
            return 0.0;
        }

        $baseDiscount = $subtotal * $this->discountPercentage / 100.0;

        return $this->bulkDiscountEligible() ? $baseDiscount * 1.15 : $baseDiscount;
    }

    private function calculateTax(float $amount): float
    {
        return $amount * $this->taxRate;
    }

    private function totalItemCount(): int
    {
        $count = 0;

        foreach ($this->orderItems as $item) {
            $count += $item['quantity'] ?? $item->quantity ?? 0;
        }

        return $count;
    }

    private function validateItemData($unitPrice, $quantity): void
    {
        if (!is_numeric($unitPrice) || $unitPrice <= 0) {
            throw new InvalidArgumentException("Invalid unit_price: {$unitPrice}");
        }

        if (!is_int($quantity) || $quantity <= 0) {
            throw new InvalidArgumentException("Invalid quantity: {$quantity}");
        }
    }

    private function formatCurrency(float $amount): string
    {
        return sprintf('%.2f', $amount);
    }
}

class ServiceResult
{
    public bool $success;
    public ?array $data;
    public array $errors;

    public function __construct(bool $success, ?array $data = null, array $errors = [])
    {
        $this->success = $success;
        $this->data = $data;
        $this->errors = $errors;
    }

    public function isSuccess(): bool
    {
        return $this->success;
    }

    public function isFailure(): bool
    {
        return !$this->success;
    }
}
