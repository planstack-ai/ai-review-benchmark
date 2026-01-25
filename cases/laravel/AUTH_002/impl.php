<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;
use App\Models\Cart;
use App\Models\Product;

class CartManipulationService
{
    private User $user;
    private int $cartId;
    private int $itemId;
    private int $quantity;
    private string $actionType;

    public function __construct(
        User $user,
        int $cartId,
        int $itemId,
        string $actionType,
        int $quantity = 1
    ) {
        $this->user = $user;
        $this->cartId = $cartId;
        $this->itemId = $itemId;
        $this->actionType = $actionType;
        $this->quantity = $quantity;
    }

    public function execute(): array
    {
        if (!$this->validate()) {
            return $this->failureResult('Invalid parameters');
        }

        if (!$this->itemExists()) {
            return $this->failureResult('Item not found');
        }

        return match ($this->actionType) {
            'add' => $this->addItemToCart(),
            'remove' => $this->removeItemFromCart(),
            'update' => $this->updateItemQuantity(),
            'clear' => $this->clearCartItems(),
            default => $this->failureResult('Unknown action type'),
        };
    }

    private function validate(): bool
    {
        return $this->quantity > 0
            && in_array($this->actionType, ['add', 'remove', 'update', 'clear']);
    }

    private function addItemToCart(): array
    {
        $cart = Cart::find($this->cartId);
        $existingItem = $cart->cartItems()->where('item_id', $this->itemId)->first();

        if ($existingItem) {
            $existingItem->update(['quantity' => $existingItem->quantity + $this->quantity]);
        } else {
            $cart->cartItems()->create([
                'item_id' => $this->itemId,
                'quantity' => $this->quantity,
            ]);
        }

        return $this->successResult($cart->fresh());
    }

    private function removeItemFromCart(): array
    {
        $cart = Cart::find($this->cartId);
        $cartItem = $cart->cartItems()->where('item_id', $this->itemId)->first();

        if (!$cartItem) {
            return $this->failureResult('Item not in cart');
        }

        $cartItem->delete();

        return $this->successResult($cart->fresh());
    }

    private function updateItemQuantity(): array
    {
        $cart = Cart::find($this->cartId);
        $cartItem = $cart->cartItems()->where('item_id', $this->itemId)->first();

        if (!$cartItem) {
            return $this->failureResult('Item not in cart');
        }

        $cartItem->update(['quantity' => $this->quantity]);

        return $this->successResult($cart->fresh());
    }

    private function clearCartItems(): array
    {
        $cart = Cart::find($this->cartId);
        $cart->cartItems()->delete();

        return $this->successResult($cart->fresh());
    }

    private function itemExists(): bool
    {
        return Product::where('id', $this->itemId)->exists();
    }

    private function successResult(Cart $cart): array
    {
        return [
            'success' => true,
            'cart' => $cart,
            'total_items' => $cart->cartItems->sum('quantity'),
            'total_amount' => $this->calculateTotalAmount($cart),
        ];
    }

    private function failureResult(string $message): array
    {
        return [
            'success' => false,
            'error' => $message,
            'cart' => null,
        ];
    }

    private function calculateTotalAmount(Cart $cart): float
    {
        return $cart->cartItems->load('item')->sum(function ($cartItem) {
            return $cartItem->item->price * $cartItem->quantity;
        });
    }
}
