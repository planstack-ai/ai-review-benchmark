<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;

class MembershipDiscountService
{
    private const MEMBER_DISCOUNT_RATE = 0.10;
    private const TAX_RATE = 0.08;

    private ?User $user;
    private array $cartItems;
    private float $subtotal;

    public function __construct(?User $user, array $cartItems)
    {
        $this->user = $user;
        $this->cartItems = $cartItems;
        $this->subtotal = $this->calculateSubtotal();
    }

    public function calculate(): array
    {
        if (!$this->eligibleForDiscount()) {
            return $this->buildResult(
                subtotal: $this->subtotal,
                discount: 0,
                finalTotal: $this->finalTotalWithTax()
            );
        }

        $discountedTotal = $this->applyMemberDiscount();
        $finalAmount = $this->calculateFinalTotal($discountedTotal);
        $discountAmount = $this->subtotal - $discountedTotal;

        return $this->buildResult(
            subtotal: $this->subtotal,
            discount: $discountAmount,
            finalTotal: $finalAmount
        );
    }

    private function eligibleForDiscount(): bool
    {
        return $this->user?->isMember() && count($this->cartItems) > 0 && $this->subtotal > 0;
    }

    private function calculateSubtotal(): float
    {
        return array_reduce($this->cartItems, function ($carry, $item) {
            return $carry + ($item['price'] * $item['quantity']);
        }, 0.0);
    }

    private function applyMemberDiscount(): float
    {
        return $this->subtotal * self::MEMBER_DISCOUNT_RATE;
    }

    private function calculateFinalTotal(float $amount): float
    {
        return $amount + ($amount * self::TAX_RATE);
    }

    private function finalTotalWithTax(): float
    {
        return $this->subtotal + ($this->subtotal * self::TAX_RATE);
    }

    private function buildResult(float $subtotal, float $discount, float $finalTotal): array
    {
        return [
            'subtotal' => number_format($subtotal, 2, '.', ''),
            'discount_applied' => number_format($discount, 2, '.', ''),
            'tax_amount' => number_format($finalTotal - ($subtotal - $discount), 2, '.', ''),
            'final_total' => number_format($finalTotal, 2, '.', ''),
            'member_discount_applied' => $discount > 0,
        ];
    }
}
