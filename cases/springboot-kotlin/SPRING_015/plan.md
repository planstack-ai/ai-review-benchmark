# SPRING_015: Archive orders and trigger audit

## Overview

Implement batch archival process that moves old orders to archived status and records audit trail for compliance.

## Requirements

1. Find all orders older than specified cutoff date (e.g., 90 days)
2. Update their status to "ARCHIVED"
3. Trigger audit logging for each archived order via entity listeners
4. Return count of archived orders
5. Process should be efficient for large datasets

## Constraints

- Audit logging must be triggered for compliance
- Audit log should record: order ID, old status, new status, timestamp, user
- @EntityListeners should be used for audit trail
- Process should handle thousands of orders efficiently

## References

- JPA @EntityListeners
- JPA lifecycle callbacks
- Spring Data JPA @Modifying queries
- Batch processing best practices
