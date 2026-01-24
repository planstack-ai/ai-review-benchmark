# Floating Point Currency Price Calculator

## Overview

This system calculates product prices with decimal precision for e-commerce transactions. The calculator must handle currency amounts accurately to prevent financial discrepancies in customer billing and business accounting. The system processes base prices and applies percentage-based adjustments while maintaining proper decimal precision throughout all calculations.

## Requirements

1. Accept a base price as a decimal number with up to 2 decimal places
2. Accept a percentage adjustment as a decimal number (positive or negative)
3. Calculate the adjusted price by applying the percentage to the base price
4. Return the final price rounded to exactly 2 decimal places
5. Handle percentage values as actual percentages (e.g., 15.5 means 15.5%, not 0.155)
6. Preserve precision during intermediate calculations to avoid rounding errors
7. Support both price increases (positive percentages) and discounts (negative percentages)
8. Return results as decimal numbers suitable for currency display

## Constraints

1. Base price must be a positive number greater than 0
2. Percentage adjustment can range from -100% to +1000%
3. Final calculated price must not be negative (minimum 0.00)
4. Input validation must reject non-numeric values
5. All monetary calculations must maintain precision to avoid floating-point arithmetic errors
6. Results must be formatted to exactly 2 decimal places for currency compliance

## References

See context.md for existing currency handling patterns and decimal precision requirements in the current codebase.