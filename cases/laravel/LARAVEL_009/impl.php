<?php

namespace App\Services;

use App\Models\Order;
use App\Models\OrderItem;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Log;

class OrderCalculationService
{
    public function __construct(
        private readonly string $currency = 'USD'
    ) {}

    public function calculateOrderTotals(Order $order): array
    {
        $items = $order->items()->with('product')->get();
        
        if ($items->isEmpty()) {
            return $this->getEmptyOrderTotals();
        }

        $subtotal = $this->calculateSubtotal($items);
        $taxAmount = $this->calculateTaxAmount($items);
        $shippingCost = $this->calculateShippingCost($order, $subtotal);
        $discountAmount = $this->calculateDiscountAmount($order, $subtotal);
        
        $total = $subtotal + $taxAmount + $shippingCost - $discountAmount;

        return [
            'subtotal' => round($subtotal, 2),
            'tax_amount' => round($taxAmount, 2),
            'shipping_cost' => round($shippingCost, 2),
            'discount_amount' => round($discountAmount, 2),
            'total' => round($total, 2),
            'currency' => $this->currency,
            'item_count' => $items->count()
        ];
    }

    private function calculateSubtotal(Collection $items): float
    {
        return $items->sum(function (OrderItem $item) {
            return $item->quantity * $item->unit_price;
        });
    }

    private function calculateTaxAmount(Collection $items): float
    {
        $taxAmount = 0;

        foreach ($items as $item) {
            $itemTotal = $item->quantity * $item->unit_price;
            $taxRate = config('shop.tax_rate', 0.08);
            
            if ($this->isItemTaxable($item)) {
                $taxAmount += $itemTotal * $taxRate;
            }
        }

        return $taxAmount;
    }

    private function calculateShippingCost(Order $order, float $subtotal): float
    {
        $freeShippingThreshold = config('shop.free_shipping_threshold', 100.00);
        
        if ($subtotal >= $freeShippingThreshold) {
            return 0;
        }

        $baseShippingRate = config('shop.base_shipping_rate', 9.99);
        $shippingMultiplier = $this->getShippingMultiplier($order->shipping_method);
        
        return $baseShippingRate * $shippingMultiplier;
    }

    private function calculateDiscountAmount(Order $order, float $subtotal): float
    {
        if (!$order->coupon_code) {
            return 0;
        }

        $discountRate = $this->getDiscountRate($order->coupon_code);
        $maxDiscount = config('shop.max_discount_amount', 50.00);
        
        $discountAmount = $subtotal * $discountRate;
        
        return min($discountAmount, $maxDiscount);
    }

    private function isItemTaxable(OrderItem $item): bool
    {
        $taxExemptCategories = config('shop.tax_exempt_categories', []);
        
        return !in_array($item->product->category_id, $taxExemptCategories);
    }

    private function getShippingMultiplier(string $method): float
    {
        return match ($method) {
            'express' => 2.5,
            'overnight' => 4.0,
            'international' => 3.2,
            default => 1.0
        };
    }

    private function getDiscountRate(string $couponCode): float
    {
        $validCoupons = config('shop.valid_coupons', []);
        
        return $validCoupons[$couponCode] ?? 0;
    }

    private function getEmptyOrderTotals(): array
    {
        return [
            'subtotal' => 0.00,
            'tax_amount' => 0.00,
            'shipping_cost' => 0.00,
            'discount_amount' => 0.00,
            'total' => 0.00,
            'currency' => $this->currency,
            'item_count' => 0
        ];
    }
}