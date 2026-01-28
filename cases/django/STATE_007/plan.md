# Delivery Status Progression System

## Overview

The delivery status system manages the lifecycle of package deliveries through a series of predefined states. Each delivery must progress through these states in a specific order to maintain data integrity and provide accurate tracking information to customers. The system prevents regression to previous states to ensure the delivery timeline remains consistent and reliable.

## Requirements

1. Define a delivery status model with the following sequential states: PENDING, CONFIRMED, SHIPPED, OUT_FOR_DELIVERY, DELIVERED, RETURNED
2. Implement status transition validation that only allows forward progression through the defined sequence
3. Prevent any backward transitions from a higher status to a lower status in the sequence
4. Raise appropriate validation errors when invalid status transitions are attempted
5. Allow the same status to be set multiple times (idempotent operations)
6. Provide a method to check if a status transition is valid before attempting the change
7. Store the current delivery status with timestamp tracking for audit purposes
8. Ensure status changes are atomic and consistent across the system

## Constraints

1. Status transitions must be validated at the model level, not just in views or forms
2. The RETURNED status can only be reached from DELIVERED status
3. Once a delivery reaches DELIVERED status, it cannot transition to any other status except RETURNED
4. Status field must be required and cannot be null or empty
5. Invalid status values outside the defined sequence must be rejected
6. The system must handle concurrent status updates gracefully

## References

See context.md for existing delivery model structure and related implementations.