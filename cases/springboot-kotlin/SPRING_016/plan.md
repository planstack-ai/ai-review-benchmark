# SPRING_016: Load only needed order fields for report

## Overview

Implement sales report generation that provides summary statistics of orders including order ID, total amount, and order date.

## Requirements

1. Generate report with following fields for each order:
   - Order ID
   - Total amount
   - Order date
2. Report should include all orders in the system
3. Report generation should be fast and memory-efficient
4. No need for order items, customer details, or other related data

## Constraints

- Report may contain thousands of orders
- System has limited memory (container with 512MB heap)
- Response time should be under 2 seconds
- Only summary fields needed, not full order details

## References

- JPA projections
- Spring Data JPA interface-based projections
- DTO projections with @Query
- Performance optimization techniques
