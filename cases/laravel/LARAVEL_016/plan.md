# Delivery Date Calculator Service

## Overview

The system needs to calculate accurate delivery dates for customer orders based on the order placement date. This is a critical business function that affects customer expectations and logistics planning. The service must handle various delivery timeframes and ensure dates are calculated consistently across different time zones and business scenarios.

## Requirements

1. Create a service class that calculates delivery dates based on order dates
2. Support multiple delivery timeframes (standard, express, overnight)
3. Standard delivery should add 5 business days to the order date
4. Express delivery should add 2 business days to the order date
5. Overnight delivery should add 1 business day to the order date
6. Business days should exclude weekends (Saturday and Sunday)
7. The service should accept Carbon date instances as input
8. The service should return Carbon date instances as output
9. All date calculations must preserve the original order date for audit purposes
10. The service should handle edge cases where delivery dates fall on weekends by moving to the next business day

## Constraints

1. Input order dates must be valid Carbon instances
2. Delivery type must be one of: 'standard', 'express', 'overnight'
3. Order dates cannot be in the future beyond current date
4. The system must maintain immutability of input date objects
5. Weekend adjustments should only move dates forward, never backward
6. All dates should maintain consistent timezone handling

## References

See context.md for existing date handling patterns and Carbon usage examples in the codebase.