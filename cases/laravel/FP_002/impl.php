<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Order;
use App\Models\User;
use App\Models\Product;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class OrderProcessingService
{
    private User $user;
    private array $items;
    private ?Order $order = null;

    public function __construct(User $user, array $items)
    {
        $this->user = $user;
        $this->items = $items;
    }

    public function process(): array
    {
        try {
            DB::beginTransaction();

            $this->validateItems();
            $this->createOrder();
            $this->createOrderItems();
            $this->updateInventory();

            DB::commit();

            Log::info("Order {$this->order->id} processed successfully for user {$this->user->id}");

            return [
                'success' => true,
                'order' => $this->order,
                'message' => 'Order processed successfully',
            ];
        } catch (\Exception $e) {
            DB::rollBack();

            Log::error("Order processing failed: {$e->getMessage()}");

            return [
                'success' => false,
                'order' => null,
                'message' => $e->getMessage(),
            ];
        }
    }

    private function validateItems(): void
    {
        foreach ($this->items as $item) {
            $product = Product::find($item['product_id']);

            if (!$product) {
                throw new \Exception("Product {$item['product_id']} not found");
            }

            if (!$product->active) {
                throw new \Exception("Product {$product->name} is not available");
            }

            if ($product->stock < $item['quantity']) {
                throw new \Exception("Insufficient stock for {$product->name}");
            }
        }
    }

    private function createOrder(): void
    {
        $subtotal = $this->calculateSubtotal();
        $taxAmount = $this->calculateTax($subtotal);

        $this->order = Order::create([
            'user_id' => $this->user->id,
            'subtotal' => $subtotal,
            'tax_amount' => $taxAmount,
            'total' => $subtotal + $taxAmount,
            'status' => 'pending',
        ]);
    }

    private function createOrderItems(): void
    {
        foreach ($this->items as $item) {
            $product = Product::find($item['product_id']);

            $this->order->orderItems()->create([
                'product_id' => $product->id,
                'quantity' => $item['quantity'],
                'unit_price' => $product->price,
            ]);
        }
    }

    private function updateInventory(): void
    {
        foreach ($this->items as $item) {
            Product::where('id', $item['product_id'])
                ->where('stock', '>=', $item['quantity'])
                ->decrement('stock', $item['quantity']);
        }
    }

    private function calculateSubtotal(): float
    {
        return collect($this->items)->sum(function ($item) {
            $product = Product::find($item['product_id']);
            return $product->price * $item['quantity'];
        });
    }

    private function calculateTax(float $subtotal): float
    {
        return round($subtotal * 0.10, 2);
    }
}
