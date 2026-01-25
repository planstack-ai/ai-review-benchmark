# Expected Critique

## Performance Bug: Cart Nested N+1 Queries

### Location
`getCart()` method:
```php
$items = CartItem::where('cart_id', $cart->id)->get();

foreach ($items as $item) {
    $product = Product::find($item->product_id); // N queries
    $categoryName = $product->category->name;     // Another N queries
}
```

### Problem
For a cart with 10 items:
- 1 query for cart items
- 10 queries for products
- 10 queries for categories
- **Total: 21 queries** instead of 1-2

This runs on every cart page view and add-to-cart action.

### Impact
1. **Slow cart page**: Multiple round-trips to database
2. **Poor UX**: Cart updates feel sluggish
3. **High latency**: Especially noticeable on high-latency DB connections
4. **Multiplied on actions**: addItem() calls getCart(), doubling the issue

### Correct Implementation
```php
public function getCart(int $userId): array
{
    $cart = Cart::firstOrCreate(['user_id' => $userId]);

    // Single query with nested eager loading
    $items = CartItem::with(['product.category'])
        ->where('cart_id', $cart->id)
        ->get();

    $cartItems = [];
    $subtotal = 0;

    foreach ($items as $item) {
        // Already loaded - no additional queries
        $product = $item->product;
        $itemTotal = $product->price * $item->quantity;

        $cartItems[] = [
            'id' => $item->id,
            'product_id' => $product->id,
            'product_name' => $product->name,
            'category' => $product->category->name,
            'price' => $product->price,
            'quantity' => $item->quantity,
            'total' => $itemTotal,
        ];

        $subtotal += $itemTotal;
    }

    return [...];
}
```

### Severity: Medium
Affects every cart page load and cart modification.
