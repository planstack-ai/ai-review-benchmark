# Expected Critique

## Essential Finding

The `addItemToCart` method immediately reserves stock when items are added to the cart via `reserveStockForItem`. This causes stock lockup for abandoned carts and can make products appear out of stock when they're actually available.

## Key Points to Mention

1. **Bug Location**: `reserveStockForItem($product, $quantity)` is called inside `addItemToCart` instead of during checkout.

2. **Stock Lockup Problem**: When users add items to cart but don't complete purchase, the stock remains reserved (locked) for 30 minutes, blocking other customers.

3. **Correct Implementation**: Stock reservation should happen only during `processCheckout`, not `addItemToCart`. Validate availability at cart time but don't reserve.

4. **Business Impact**: Popular items may appear "out of stock" even when available because abandoned carts hold reservations.

5. **Scalability Issue**: During high-traffic events (sales, holidays), this causes massive phantom stockouts.

## Severity Rationale

- **Lost Sales**: Customers see "out of stock" for items that are actually available, leading to lost sales.

- **Cart Abandonment Rate**: E-commerce has 70%+ cart abandonment - reserving stock at cart time locks massive amounts of inventory.

- **Customer Experience**: Users may get upset when items they carted become "unavailable" before checkout.

## Acceptable Variations

- **Different Fix Approaches**: Reviews might suggest lazy reservation (at checkout only), soft reservation (doesn't block), or shorter expiration times.

- **Terminology Variations**: The bug might be described as "premature stock reservation," "eager locking," "inventory lockup," or "cart-time reservation."

- **Impact Descriptions**: Reviews might focus on "phantom stockouts," "inventory blocking," or "abandoned cart stock impact."
