# Order Status Query Service

## Overview

Implement a service to query orders by their status. The service is used by the operations team to monitor order processing pipelines and identify orders that need attention. It must handle all orders in the system including legacy orders from before the status tracking system was implemented.

## Requirements

1. Return all orders currently in pending status awaiting processing
2. Return all orders that require attention (pending or failed status)
3. Support filtering orders by date range combined with status
4. Return counts of orders by status for dashboard metrics
5. Must include all legacy orders that haven't been processed yet

## Constraints

1. Must handle legacy orders - some older orders may not have status set
2. Legacy orders without explicit status should be treated as pending
3. Do not modify order data - this is a read-only query service
4. Performance: queries should be efficient for large order volumes

## References

See context.md for Order model, enum definition, and migration history.
