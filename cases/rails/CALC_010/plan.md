# Bulk Order Total Calculation System

## Overview

The system needs to handle bulk order calculations for e-commerce transactions where customers can purchase large quantities of items. The system must accurately calculate totals while handling various quantity scenarios including edge cases where quantities may exceed normal operational limits.

## Requirements

1. Calculate the total cost by multiplying item price by quantity
2. Accept quantity values as integers greater than zero
3. Accept price values as positive decimal numbers
4. Return the calculated total as a decimal value with appropriate precision
5. Handle standard bulk order quantities up to 10,000 units per item
6. Process orders with multiple line items independently
7. Maintain calculation accuracy for high-value transactions
8. Support quantity inputs from various sources (user input, API calls, file imports)

## Constraints

1. Quantity must be a positive integer (no negative or zero values)
2. Price must be a positive number (no negative or zero values)
3. Maximum reasonable quantity per line item should not exceed 1,000,000 units
4. Calculated totals must maintain precision to at least 2 decimal places
5. System must handle edge cases gracefully without crashing
6. Input validation must occur before calculation processing
7. Large quantity calculations must not cause system performance degradation

## References

See context.md for existing calculation patterns and validation approaches used in the current system.