# Loyalty Points Calculation System

## Overview

The system calculates loyalty points for customer purchases. Points are earned based on order total, with different rates for standard and premium members. Additional bonus points are awarded for first-time customers, large orders, and seasonal promotions. Point multipliers apply based on loyalty tier and weekend purchases.

## Requirements

1. Standard point rate: 1% of order total (0.01)
2. Premium member point rate: 2% of order total (0.02)
3. Minimum purchase of $10 required to earn points
4. Points not earned on cancelled orders
5. Points not earned for users with suspended points status
6. First-time customer bonus: 50 points
7. Orders over $100 earn 25 bonus points
8. Seasonal promotion (Nov, Dec, Jan): 0.5% additional points
9. Gold tier: 1.5x point multiplier
10. Silver tier: 1.2x point multiplier
11. Weekend bonus: 1.1x additional multiplier
12. **Points must be calculated on the final paid amount (after discounts)**

## Constraints

1. Points are calculated as whole numbers (rounded)
2. Only completed orders earn points
3. Multipliers are applied to total points (base + bonus)
4. Multiple multipliers stack multiplicatively
5. Order total used for points should be the amount actually paid

## References

See context.md for user loyalty tier definitions and order status values.
