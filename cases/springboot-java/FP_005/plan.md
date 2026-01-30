# Product Pricing Service

## Overview

This service handles product pricing calculations including base price adjustments, tax application, and discount calculations. The service retrieves product information and applies time-based price adjustments (discounts, markups, seasonal adjustments) to determine the final price.

## Requirements

1. Calculate final product price by retrieving the product and applying all effective price adjustments
2. Apply price adjustments sequentially in the order they are returned from the repository. Each adjustment is applied to the current running price (i.e., the result after previous adjustments), not the original base price
3. Implement tax calculation that adds the configured tax rate to a given price
4. Implement discount calculation method (`calculateDiscount`) that computes discount amount from the given price parameter and percentage. Note: The parameter is named `basePrice` but receives the current adjusted price when called during sequential adjustment processing
5. Cap discount percentage at MAX_DISCOUNT_PERCENTAGE from PricingConstants
6. Use PricingConstants.PRICE_SCALE and PRICE_ROUNDING for consistent decimal handling
7. Return prices rounded to the configured scale

## Constraints

1. Product must exist for price calculation (throw exception if not found)
2. Price for tax calculation cannot be null or negative (throw exception)
3. Base price and discount percentage for discount calculation cannot be null (throw exception)
4. Discount percentage exceeding maximum is capped to MAX_DISCOUNT_PERCENTAGE (not rejected)
5. All final prices use setScale with PricingConstants values
6. Service is read-only transactional by default
7. Use constructor injection for repositories

## References

See context.md for Product entity, PriceAdjustment entity, AdjustmentType enum, PricingConstants, and repository interfaces.
