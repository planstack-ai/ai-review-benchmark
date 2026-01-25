<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Cart;
use App\Models\CartItem;
use App\Models\Product;

class CartService
{
    public function getCart(int $userId): array
    {
        $cart = Cart::firstOrCreate(['user_id' => $userId]);

        // BUG: N+1 query - items loaded then product accessed in loop
        $items = CartItem::where('cart_id', $cart->id)->get();

        $cartItems = [];
        $subtotal = 0;

        foreach ($items as $item) {
            // BUG: Query per item for product
            $product = Product::find($item->product_id);

            // BUG: Another query for category
            $categoryName = $product->category->name;

            $itemTotal = $product->price * $item->quantity;

            $cartItems[] = [
                'id' => $item->id,
                'product_id' => $product->id,
                'product_name' => $product->name,
                'category' => $categoryName,
                'price' => $product->price,
                'quantity' => $item->quantity,
                'total' => $itemTotal,
            ];

            $subtotal += $itemTotal;
        }

        return [
            'cart_id' => $cart->id,
            'items' => $cartItems,
            'subtotal' => $subtotal,
            'item_count' => count($cartItems),
        ];
    }

    public function addItem(int $userId, int $productId, int $quantity): array
    {
        $cart = Cart::firstOrCreate(['user_id' => $userId]);

        // BUG: Doesn't check if product exists before adding
        // Also queries product just to check it exists
        $product = Product::findOrFail($productId);

        $existingItem = CartItem::where('cart_id', $cart->id)
            ->where('product_id', $productId)
            ->first();

        if ($existingItem) {
            $existingItem->increment('quantity', $quantity);
        } else {
            CartItem::create([
                'cart_id' => $cart->id,
                'product_id' => $productId,
                'quantity' => $quantity,
            ]);
        }

        // BUG: Returns full cart which triggers all the N+1 queries again
        return $this->getCart($userId);
    }

    public function updateQuantity(int $userId, int $itemId, int $quantity): array
    {
        $cart = Cart::where('user_id', $userId)->firstOrFail();

        CartItem::where('id', $itemId)
            ->where('cart_id', $cart->id)
            ->update(['quantity' => $quantity]);

        return $this->getCart($userId);
    }
}
