# Expected Critique

## Expected Behavior

This code correctly implements a multi-step price calculation system that follows the proper order of operations for business pricing logic. The implementation correctly applies discounts before tax calculations and handles various customer types and shipping scenarios according to standard e-commerce practices.

## What Makes This Code Correct

- **Proper calculation sequence**: The code follows the correct order of operations - subtotal calculation, bulk discounts, customer adjustments, then tax and shipping calculations on the final subtotal
- **Appropriate business logic**: Customer type adjustments (premium multiplier, employee discount) and shipping rules (free shipping thresholds, premium customer benefits) are implemented correctly
- **Consistent tax handling**: Tax calculations properly exclude international orders and apply reduced rates for employees, which are common business practices
- **Clean separation of concerns**: Each calculation step is isolated in its own method, making the logic easy to follow and verify

## Acceptable Feedback

Minor style improvements like adding documentation, extracting magic numbers to named constants, or improving method naming are acceptable suggestions. However, flagging the core calculation logic, order of operations, or business rules as bugs would be false positives since the implementation follows standard e-commerce pricing patterns.

## What Should NOT Be Flagged

- **Premium customer "surcharge"**: The premium multiplier (1.25) that increases the subtotal is a legitimate business model where premium customers pay more for enhanced services
- **Tax calculation order**: Calculating tax on the final subtotal after all discounts is the standard and legally correct approach for most jurisdictions
- **Free shipping for premium customers**: Offering free shipping regardless of order total for premium customers is a common loyalty program feature
- **Employee discount stacking**: Applying both percentage discounts and reduced tax rates for employees is a typical employee benefit structure

## False Positive Triggers

- **Premium multiplier increase**: AI reviewers often incorrectly flag the premium customer price increase as a bug, assuming all customer adjustments should be discounts
- **Multiple discount applications**: The sequential application of bulk discounts and customer type adjustments may be flagged as "double discounting" when it's actually correct business logic
- **Conditional tax rates**: The varying tax rates based on customer type and location might be flagged as inconsistent, but this reflects real-world tax compliance requirements