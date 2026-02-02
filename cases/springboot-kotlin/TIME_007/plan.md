# Business Day Delivery Date Calculator

## Overview

The shipping service needs to calculate estimated delivery dates based on business days rather than calendar days. This is critical for setting accurate customer expectations, as deliveries do not occur on weekends or holidays. The system must provide a reliable way to calculate when an order will arrive based on the number of business days required for processing and shipping.

## Requirements

1. Implement a method to calculate the delivery date by adding a specified number of business days to a start date
2. Business days are defined as Monday through Friday only
3. Weekends (Saturday and Sunday) should not be counted as business days
4. When calculating N business days from a date, only count weekdays and skip weekend days
5. For example, adding 3 business days to a Friday should result in the following Wednesday (skipping Saturday and Sunday)
6. The calculation should handle cases where the start date itself falls on a weekend
7. Return the final delivery date after accounting for all business days

## Constraints

1. Input dates are provided as LocalDate
2. The number of business days to add must be a positive integer
3. Weekend days (Saturday and Sunday) must be excluded from the business day count
4. The implementation should handle multiple weeks if necessary (e.g., 10 business days spans two calendar weeks)
5. If the start date falls on a weekend, begin counting from the next Monday
6. The resulting delivery date should always fall on a weekday (Monday-Friday)
7. Holidays are not considered in this initial implementation (to be added in future versions)

## References

See context.md for existing shipping and delivery entity structure.
