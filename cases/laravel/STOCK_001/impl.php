<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;
use App\Models\Cart;
use App\Models\Product;
use App\Models\CartItem;
use App\Models\StockReservation;
use Illuminate\Support\Facades\DB;

class StockAllocationService
{
    private User $user;
    private Cart $cart;

    public function __construct(User $user)
    {
        $this->user = $user;
        $this->cart = $user->cart ?? Cart::create(['user_id' => $user->id]);
    }

    public function addItemToCart(Product $product, int $quantity): bool
    {
        if (!$product->available) {
            return false;
        }

        try {
            DB::transaction(function () use ($product, $quantity) {
                $cartItem = $this->findOrInitializeCartItem($product);
                $newQuantity = $cartItem->quantity + $quantity;

                $this->validateStockAvailability($product, $newQuantity);
                $this->reserveStockForItem($product, $quantity);

                $cartItem->quantity = $newQuantity;
                $cartItem->save();

                $this->updateCartTotals();
            });

            return true;
        } catch (\Exception $e) {
            return false;
        }
    }

    public function removeItemFromCart(Product $product, ?int $quantity = null): bool
    {
        $cartItem = $this->cart->cartItems()->where('product_id', $product->id)->first();

        if (!$cartItem) {
            return false;
        }

        DB::transaction(function () use ($product, $cartItem, $quantity) {
            $quantityToRemove = $quantity ?? $cartItem->quantity;
            $this->releaseReservedStock($product, $quantityToRemove);

            if ($quantity && $cartItem->quantity > $quantity) {
                $cartItem->decrement('quantity', $quantity);
            } else {
                $cartItem->delete();
            }

            $this->updateCartTotals();
        });

        return true;
    }

    public function processCheckout(): bool
    {
        if ($this->cart->cartItems->isEmpty()) {
            return false;
        }

        try {
            DB::transaction(function () {
                $this->validateAllReservations();
                $this->createOrderFromCart();
                $this->clearCartAndReservations();
            });

            return true;
        } catch (\Exception $e) {
            return false;
        }
    }

    private function findOrInitializeCartItem(Product $product): CartItem
    {
        return $this->cart->cartItems()->firstOrCreate(
            ['product_id' => $product->id],
            ['quantity' => 0, 'unit_price' => $product->price]
        );
    }

    private function validateStockAvailability(Product $product, int $requestedQuantity): void
    {
        $availableStock = $product->stock_quantity - $product->reserved_quantity;

        if ($availableStock < $requestedQuantity) {
            throw new \Exception('Insufficient stock');
        }
    }

    private function reserveStockForItem(Product $product, int $quantity): void
    {
        $product->increment('reserved_quantity', $quantity);

        StockReservation::create([
            'user_id' => $this->user->id,
            'product_id' => $product->id,
            'quantity' => $quantity,
            'expires_at' => now()->addMinutes(30),
        ]);
    }

    private function releaseReservedStock(Product $product, int $quantity): void
    {
        $product->decrement('reserved_quantity', $quantity);

        $reservation = StockReservation::where([
            'user_id' => $this->user->id,
            'product_id' => $product->id,
        ])->first();

        if ($reservation) {
            if ($reservation->quantity <= $quantity) {
                $reservation->delete();
            } else {
                $reservation->decrement('quantity', $quantity);
            }
        }
    }

    private function validateAllReservations(): void
    {
        foreach ($this->cart->cartItems as $item) {
            $this->validateStockAvailability($item->product, $item->quantity);
        }
    }

    private function createOrderFromCart(): void
    {
        // Order creation logic
    }

    private function clearCartAndReservations(): void
    {
        StockReservation::where('user_id', $this->user->id)->delete();
        $this->cart->cartItems()->delete();
        $this->cart->update(['total_amount' => 0]);
    }

    private function updateCartTotals(): void
    {
        $total = $this->cart->cartItems->sum(fn($item) => $item->quantity * $item->unit_price);
        $this->cart->update(['total_amount' => $total]);
    }
}
