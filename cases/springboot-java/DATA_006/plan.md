# Customer Loyalty Points Feature

## Overview

Adding a new loyalty points feature to the customer entity. Existing customers should be initialized with zero points, and the system must handle the points field consistently.

## Requirements

1. Track loyalty points for each customer
2. Existing customers should start with 0 points
3. Points can be earned and redeemed
4. Points balance should never be null
5. Display points balance on customer profile

## Constraints

1. Existing data migration must be handled
2. No NullPointerException when accessing points
3. Points cannot be negative
4. Must work with existing customers (data migration)

## References

See context.md for migration strategy.
