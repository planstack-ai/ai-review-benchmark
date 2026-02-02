# Delivery Date Validation System

## Overview

The system must validate that delivery dates for orders are scheduled for future dates only. This ensures that customers cannot select delivery dates that have already passed, maintaining operational feasibility and preventing scheduling conflicts. The validation should occur when orders are created or updated with delivery date information.

## Requirements

1. All delivery dates must be set to a date that occurs after the current date
2. The validation must trigger during order creation when a delivery date is provided
3. The validation must trigger during order updates when the delivery date is modified
4. When validation fails, the system must prevent the order from being saved
5. When validation fails, the system must display a clear error message to the user
6. The validation must account for timezone considerations when comparing dates
7. The current date comparison must use the server's current date and time
8. The validation must handle both date and datetime formats for delivery dates

## Constraints

1. Delivery dates cannot be set to today's date - they must be strictly in the future
2. The validation must work regardless of the time of day the order is placed
3. Null or empty delivery dates should be handled appropriately (either allowed or rejected based on business rules)
4. The validation must be consistent across different user interfaces (web, API, admin panel)
5. Date comparisons must be performed at the date level, not including time components for user-provided dates
6. The system must handle edge cases such as orders placed near midnight

## References

See context.md for existing validation patterns and date handling implementations in the current codebase.