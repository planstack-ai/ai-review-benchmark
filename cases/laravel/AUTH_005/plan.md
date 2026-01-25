# Product Pricing Service

## Overview

The system calculates product prices with different pricing tiers. Members get special member pricing when available, while non-members pay regular prices. Quantity discounts apply based on order volume.

## Requirements

1. Determine correct unit price based on user membership
2. Members get member_price when available
3. Non-members pay regular_price
4. Apply quantity discounts (5%: 5-9, 10%: 10-19, 15%: 20+)
5. Return pricing breakdown with tier information
6. **Guest users (not logged in) must NOT get member pricing**
7. Handle products without member pricing enabled

## Constraints

1. Member pricing requires verified membership status
2. Quantity discounts only apply if enabled on product
3. Guest users should always pay regular price
4. User must be logged in AND have member status for member pricing

## References

See context.md for User membership status and Product pricing fields.
