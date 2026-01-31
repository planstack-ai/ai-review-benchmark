<?php

namespace App\Services;

use App\Models\Customer;
use App\Models\Product;
use App\Models\Order;
use Illuminate\Support\Facades\Config;

class PriceCalculationService
{
    public function __construct(
        private readonly float $taxRate = 0.08
    ) {}

    public function calculateOrderTotal(Order $order): array
    {
        $subtotal = $this->calculateSubtotal($order);
        $quantityDiscount = $this->calculateQuantityDiscount($subtotal, $order->quantity);
        $discountedSubtotal = $subtotal - $quantityDiscount;
        
        $customerAdjustment = $this->calculateCustomerAdjustment($discountedSubtotal, $order->customer);
        $adjustedSubtotal = $discountedSubtotal + $customerAdjustment;
        
        $tax = $this->calculateTax($adjustedSubtotal);
        $total = $adjustedSubtotal + $tax;

        return [
            'subtotal' => round($subtotal, 2),
            'quantity_discount' => round($quantityDiscount, 2),
            'customer_adjustment' => round($customerAdjustment, 2),
            'tax' => round($tax, 2),
            'total' => round($total, 2)
        ];
    }

    private function calculateSubtotal(Order $order): float
    {
        return $order->product->price * $order->quantity;
    }

    private function calculateQuantityDiscount(float $subtotal, int $quantity): float
    {
        if ($quantity >= 100) {
            return $subtotal * 0.15;
        }
        
        if ($quantity >= 50) {
            return $subtotal * 0.10;
        }
        
        if ($quantity >= 20) {
            return $subtotal * 0.05;
        }

        return 0.0;
    }

    private function calculateCustomerAdjustment(float $amount, Customer $customer): float
    {
        return match ($customer->type) {
            'premium' => $amount * 0.05,
            'standard' => 0.0,
            'budget' => -($amount * 0.03),
            default => 0.0
        };
    }

    private function calculateTax(float $taxableAmount): float
    {
        return $taxableAmount * $this->taxRate;
    }

    public function getDiscountBreakdown(Order $order): array
    {
        $subtotal = $this->calculateSubtotal($order);
        $quantityDiscount = $this->calculateQuantityDiscount($subtotal, $order->quantity);
        
        return [
            'quantity_discount_rate' => $this->getQuantityDiscountRate($order->quantity),
            'quantity_discount_amount' => round($quantityDiscount, 2),
            'customer_type' => $order->customer->type,
            'customer_adjustment_rate' => $this->getCustomerAdjustmentRate($order->customer->type)
        ];
    }

    private function getQuantityDiscountRate(int $quantity): float
    {
        if ($quantity >= 100) return 0.15;
        if ($quantity >= 50) return 0.10;
        if ($quantity >= 20) return 0.05;
        return 0.0;
    }

    private function getCustomerAdjustmentRate(string $customerType): float
    {
        return match ($customerType) {
            'premium' => 0.05,
            'standard' => 0.0,
            'budget' => -0.03,
            default => 0.0
        };
    }
}