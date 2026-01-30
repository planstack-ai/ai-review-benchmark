# Monthly Sales Report Generation

## Overview

The system generates monthly sales reports for business analytics. The report aggregates order data across all orders in the system to calculate total revenue, order counts, and trends.

## Requirements

1. Generate monthly aggregated sales data
2. Calculate total revenue across all orders
3. Count orders by status
4. Handle large datasets efficiently (production has 1M+ orders)

## Constraints

1. Report generation must complete within reasonable time
2. Memory usage must be bounded
3. Must not impact production database performance significantly
