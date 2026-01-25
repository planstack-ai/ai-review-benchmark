# Expected Critique

## Essential Finding

The code contains a critical state validation bug where orders can be cancelled even after they have been shipped. The `validate_order_status!` method checks for cancelled and completed orders but fails to verify if the order has already been shipped, violating the fundamental business rule that shipped orders cannot be cancelled.

## Key Points to Mention

1. **Missing shipment status check**: The `validate_order_status!` method does not include a check for `order.shipped?` before allowing cancellation to proceed.

2. **Incorrect state transition**: The current implementation allows invalid state transitions from "shipped" to "cancelled", which should be prohibited by business logic.

3. **Required fix**: Add `raise CannotCancelError, 'Cannot cancel shipped order' if order.shipped?` to the `validate_order_status!` method before the existing validations.

4. **Business impact**: This bug allows customers to cancel orders that have already left the warehouse, leading to delivery of unpaid goods, inventory discrepancies, and potential financial losses.

5. **Transaction integrity**: The bug undermines the order lifecycle by allowing cancellations at inappropriate states, potentially causing downstream processing issues with refunds and inventory management.

## Severity Rationale

- **Direct financial impact**: Shipped orders that get cancelled result in delivered goods without payment, causing immediate revenue loss and potential chargebacks
- **Operational disruption**: Invalid cancellations create conflicts between physical shipments and system state, requiring manual intervention and customer service escalation
- **Business rule violation**: Core constraint that cancellations must occur before shipment is completely bypassed, undermining the entire order fulfillment process

## Acceptable Variations

- Could describe the issue as "missing shipped status validation" or "inadequate order state checking" rather than specifically mentioning the shipment check
- Might suggest alternative implementation approaches like using a state machine or enum-based validation instead of individual boolean checks
- Could focus on the race condition aspect where orders might be cancelled while shipping is in progress, requiring atomic state checking