# Refund Processing Service

## Overview

This service implements refund processing for an e-commerce platform. When orders are refunded, the payment status must be updated correctly to reflect the refund state.

## Requirements

1. Process refund requests for completed orders
2. Update payment status after successful refund
3. Record refund transaction details
4. Notify customer of refund completion
5. Handle partial refunds
6. Support multiple payment methods
7. Maintain audit trail of refund operations
8. Calculate refund amount including any fees

## Constraints

1. Only paid orders can be refunded
2. Payment status must reflect refund state
3. Refund amount cannot exceed original payment
4. Refund must be processed within business rules
5. The service should be transactional
6. Multiple refunds on same order must be tracked

## References

See context.md for existing payment management patterns in the codebase.
