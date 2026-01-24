# Past Delivery Date Validation

## Overview

The system must validate that delivery dates are scheduled for future dates only. This ensures that customers cannot place orders with delivery dates that have already passed, which would be logistically impossible to fulfill. The validation should prevent order processing when delivery dates are set to today or any past date.

## Requirements

1. All delivery dates must be strictly in the future (after the current date)
2. Delivery dates set to today's date must be rejected
3. Delivery dates set to any past date must be rejected
4. The system must use the current system date/time for comparison
5. Validation must occur before order processing begins
6. Clear error messages must be provided when validation fails
7. The validation must handle timezone considerations appropriately
8. Date comparison must account for the full date (not just day/month/year)

## Constraints

- Delivery dates cannot be null or empty
- The system must handle edge cases around midnight transitions
- Validation must be consistent across different server timezones
- The current date reference point must be determined at validation time, not cached
- Date format must be properly parsed before validation
- Invalid date formats should be handled gracefully

## References

See context.md for existing date validation patterns and delivery scheduling implementations in the codebase.