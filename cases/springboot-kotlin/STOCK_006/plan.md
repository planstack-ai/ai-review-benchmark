# Stock Restoration with Capacity Limits

## Overview

This system manages order cancellations and stock restoration for an e-commerce platform. When a customer cancels an order, the system must restore the purchased items back to inventory. However, each product has a maximum storage capacity, and the restoration process must not cause the stock level to exceed this capacity limit. This is particularly important for perishable goods or warehouse space limitations.

## Requirements

1. The system shall provide an endpoint to cancel orders and restore stock
2. When an order is cancelled, the quantities of all items must be restored to inventory
3. Each product has a maximum stock capacity that cannot be exceeded
4. The stock restoration process must check that restored quantities do not exceed max capacity
5. If restoration would exceed capacity, the stock should be set to the maximum allowed value
6. The system must track both current stock levels and maximum capacity per product
7. Stock restoration must handle partial restoration when capacity is limited
8. Clear logging must be provided when stock restoration is capped at maximum capacity
9. The cancellation process must be atomic and handle all items in the order
10. The system shall prevent inventory levels from becoming invalid due to cancellations

## Constraints

1. Product stock quantities must never exceed the defined maximum capacity
2. Maximum capacity values must be positive integers greater than zero
3. Current stock levels must be between 0 and maximum capacity (inclusive)
4. Order IDs must be valid and reference existing orders
5. Only orders in certain statuses can be cancelled
6. The restoration logic must be idempotent to prevent duplicate stock increases
7. Database constraints should enforce the maximum capacity limit

## References

See context.md for existing order cancellation implementations, inventory management patterns, and database schema details.
