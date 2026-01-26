# Delivery Date Validation System

## Overview

The system must validate delivery dates for orders to ensure they are scheduled for future dates only. This prevents logistical issues and ensures proper order fulfillment scheduling. The validation should occur when delivery dates are set or updated, providing clear feedback when invalid dates are provided.

## Requirements

1. All delivery dates must be set to a future date (after the current date)
2. The system must reject delivery dates that are today's date or any past date
3. Validation must occur when creating new delivery records
4. Validation must occur when updating existing delivery dates
5. Clear error messages must be provided when validation fails
6. The validation must use the server's current date and time for comparison
7. The system must handle timezone considerations appropriately
8. Validation errors must prevent the record from being saved to the database

## Constraints

1. Date comparison must account for time zones to ensure accurate validation
2. The validation must be performed at the model level to ensure data integrity
3. Error messages must be user-friendly and indicate the specific validation failure
4. The system must handle edge cases such as leap years and month boundaries
5. Validation must be consistent across different date input formats
6. The current date reference must be dynamic (not hardcoded)

## References

See context.md for existing model implementations and related validation patterns in the codebase.