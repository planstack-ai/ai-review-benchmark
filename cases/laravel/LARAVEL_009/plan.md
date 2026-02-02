# Order Calculation Service Implementation

## Overview

This feature implements a service class that calculates order totals including subtotal, tax, shipping, and discounts. The service needs to process order items and apply various configuration-based rates efficiently for production environments with potentially large orders.

## Requirements

1. Create a service class that calculates complete order totals
2. Calculate subtotal from order items (quantity * unit_price)
3. Calculate tax amounts based on configurable tax rate from Laravel's config system
4. Determine shipping costs with free shipping threshold and shipping method multipliers
5. Apply discount amounts based on coupon codes with a maximum discount cap
6. Support tax-exempt product categories
7. Handle empty orders gracefully
8. Return a comprehensive totals array with all calculated values

## Constraints

1. Tax rate must be retrieved from Laravel's configuration system
2. All monetary calculations should be rounded to 2 decimal places
3. The service should handle orders with many items efficiently
4. Configuration values (tax_rate, shipping thresholds, etc.) should be accessed efficiently
5. The service should work correctly when configuration caching is enabled

## Implementation Notes

- Use Laravel's `config()` helper to retrieve configuration values
- Consider performance when iterating over large collections of order items
- Configuration values that don't change during a request should be retrieved once, not repeatedly

## References

See context.md for examples of existing order processing patterns and configuration usage in the codebase.
