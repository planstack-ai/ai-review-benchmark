# Delivery Status Management Service

## Overview

This service manages delivery status updates for an e-commerce platform. Delivery status should only progress forward through defined states and never regress to previous states.

## Requirements

1. Update delivery status through defined progression
2. Validate status transitions are forward-only
3. Record status change timestamps
4. Notify customer of status updates
5. Support tracking number association
6. Log all status changes for audit
7. Handle delivery exceptions and delays
8. Support estimated delivery time updates

## Constraints

1. Status can only move forward (e.g., SHIPPED -> DELIVERED, not reverse)
2. Delivered status is final and cannot change
3. Each status change must be recorded with timestamp
4. Invalid transitions must be rejected
5. The service should be transactional
6. Status changes must trigger appropriate notifications

## References

See context.md for existing delivery management patterns in the codebase.
