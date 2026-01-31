# FP_006: Complex Nested Transaction

## Overview
Implement a payment processing service that requires nested transactions with independent commit/rollback boundaries. The outer transaction handles the main order, while inner transactions handle audit logging and notification queuing that must succeed regardless of order processing outcome.

## Requirements
1. Process order payment in outer transaction
2. Log audit trail in independent transaction (must commit even if order fails)
3. Queue notifications in independent transaction (must commit even if order fails)
4. Use `@Transactional(propagation = Propagation.REQUIRES_NEW)` for independent transactions
5. Ensure audit and notification records persist even when order processing is rolled back

## Why This Looks Suspicious But Is Correct
- **Nested transactions** with `REQUIRES_NEW` can appear problematic
- However, this is the **correct pattern** for ensuring audit logs and notifications persist independently
- The pattern ensures **data integrity** by separating concerns:
  - Order processing can fail and rollback without losing audit trail
  - Notifications are guaranteed to be queued for retry logic
  - Each transaction boundary is explicitly controlled for business requirements

## Implementation Notes
- Use `@Transactional(propagation = Propagation.REQUIRES_NEW)` for audit and notification methods
- Outer transaction uses default `REQUIRED` propagation
- This is a standard enterprise pattern for separating critical logging from business operations
