# Member Discount Rate Application System

## Overview

The system needs to provide a discount mechanism for members of the platform. When members make purchases or transactions, they should receive a 10% discount on their total amount. This feature is part of the broader customer loyalty program designed to incentivize membership and increase customer retention.

## Requirements

1. The system must identify when a user has member status
2. A 10% discount rate must be applied to the total amount for members
3. Non-members must not receive any discount (0% discount rate)
4. The discount calculation must be applied before final amount determination
5. The system must handle decimal precision appropriately for monetary calculations
6. Member status verification must be performed for each transaction
7. The discount rate must be configurable as a constant value of 10%
8. The final discounted amount must be returned as the result

## Constraints

1. Discount rates must be expressed as percentages (0-100 range)
2. Member status must be a boolean value
3. Input amounts must be positive numbers
4. The system must handle edge cases where amount is zero
5. Discount calculations must not result in negative final amounts
6. The discount rate constant must not be hardcoded in multiple locations

## References

See context.md for existing discount calculation patterns and member verification implementations in the codebase.