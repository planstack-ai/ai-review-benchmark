# Existing Codebase

## Problem Scenario

```
1. Customer orders "Widget A" at $10.00
2. Order is saved with product_id reference
3. Later, product price is updated to $15.00
4. Customer views order history - shows $15.00 instead of $10.00!
```

## Usage Guidelines

- Snapshot immutable data at transaction time (prices, names)
- Store price_at_purchase in order_item, not just product_id
