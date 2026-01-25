<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;
use App\Models\Product;

class PricingService
{
    private ?User $user;
    private Product $product;
    private int $quantity;

    public function __construct(?User $user, Product $product, int $quantity = 1)
    {
        $this->user = $user;
        $this->product = $product;
        $this->quantity = $quantity;
    }

    public function calculateTotalPrice(): float
    {
        $unitPrice = $this->determineUnitPrice();
        $baseTotal = $unitPrice * $this->quantity;

        return $this->applyQuantityDiscounts($baseTotal);
    }

    public function pricingBreakdown(): array
    {
        $unitPrice = $this->determineUnitPrice();
        $baseTotal = $unitPrice * $this->quantity;
        $discountAmount = $this->calculateDiscountAmount($baseTotal);
        $finalTotal = $baseTotal - $discountAmount;

        return [
            'unit_price' => $unitPrice,
            'quantity' => $this->quantity,
            'base_total' => $baseTotal,
            'discount_amount' => $discountAmount,
            'final_total' => $finalTotal,
            'pricing_tier' => $this->pricingTierName(),
        ];
    }

    public function eligibleForMemberPricing(): bool
    {
        return $this->user !== null && $this->user->isMember();
    }

    private function determineUnitPrice(): float
    {
        if ($this->memberPricingApplicable()) {
            return $this->memberPrice();
        }

        return $this->regularPrice();
    }

    private function memberPricingApplicable(): bool
    {
        return $this->product->hasMemberPricingEnabled() && $this->memberPrice() !== null;
    }

    private function memberPrice(): ?float
    {
        return $this->product->member_price;
    }

    private function regularPrice(): float
    {
        return $this->product->regular_price;
    }

    private function applyQuantityDiscounts(float $baseTotal): float
    {
        $discountAmount = $this->calculateDiscountAmount($baseTotal);

        return $baseTotal - $discountAmount;
    }

    private function calculateDiscountAmount(float $baseTotal): float
    {
        if (!$this->quantityDiscountApplicable()) {
            return 0.0;
        }

        return match (true) {
            $this->quantity >= 20 => $baseTotal * 0.15,
            $this->quantity >= 10 => $baseTotal * 0.10,
            $this->quantity >= 5 => $baseTotal * 0.05,
            default => 0.0,
        };
    }

    private function quantityDiscountApplicable(): bool
    {
        return $this->quantity >= 5 && $this->product->hasQuantityDiscountsEnabled();
    }

    private function pricingTierName(): string
    {
        if ($this->memberPricingApplicable()) {
            return 'member';
        }

        return 'regular';
    }
}
