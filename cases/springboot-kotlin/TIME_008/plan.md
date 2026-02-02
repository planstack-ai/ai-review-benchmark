# Future Delivery Date Validation for Orders

## Overview

The order management system must ensure that customers can only specify delivery dates that are in the future. This validation is essential to prevent operational issues, as the system cannot deliver orders to dates that have already passed. The validation should occur when orders are created or when delivery dates are updated.

## Requirements

1. Implement validation to ensure delivery dates are always in the future
2. The validation should reject delivery dates that are today or earlier
3. Delivery dates must be at least one day after the current date
4. The validation should be applied when creating new orders
5. The validation should also be applied when updating existing order delivery dates
6. Provide clear error messages when validation fails
7. Use appropriate validation annotations to enforce this constraint at the entity level

## Constraints

1. Delivery dates are stored as LocalDate
2. The validation must compare against the current date at the time of validation
3. Today's date should be considered invalid for delivery (orders need at least one day to process)
4. The validation should be enforced at the data model level using Bean Validation annotations
5. The system should prevent orders with past or current-day delivery dates from being persisted
6. Time zone considerations should be handled appropriately for date comparisons
7. The validation must be consistent across all API endpoints that accept delivery dates

## References

See context.md for existing order entity structure and validation patterns.
