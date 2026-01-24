# Delivery Status Progression System

## Overview

The delivery status system tracks packages through their lifecycle from initial creation to final delivery. The system must enforce a strict forward progression of statuses to maintain data integrity and provide accurate tracking information to customers. Once a package reaches a certain status, it cannot regress to a previous state, ensuring the delivery timeline remains consistent and trustworthy.

## Requirements

1. The system shall support the following delivery statuses in order: `pending`, `processing`, `shipped`, `out_for_delivery`, `delivered`, `returned`

2. Status transitions shall only be allowed in the forward direction according to the defined sequence

3. A delivery status can skip intermediate statuses (e.g., `pending` can transition directly to `shipped`)

4. The system shall reject any attempt to move a delivery status backward in the sequence

5. The system shall raise an appropriate error when an invalid status transition is attempted

6. The current status shall be persisted and retrievable for each delivery record

7. Status transitions shall be atomic operations that either succeed completely or fail without partial updates

8. The system shall validate that the new status exists in the defined status list before attempting any transition

## Constraints

- A delivery with status `delivered` cannot be changed to any other status except `returned`
- A delivery with status `returned` cannot be changed to any other status
- Empty or nil status values shall not be accepted
- Status values are case-sensitive and must match exactly
- The initial status for new deliveries must be `pending`

## References

See context.md for existing delivery management implementations and related status handling patterns.