# Expected Critique

## Essential Finding

The `find_coupon` method contains a critical authorization vulnerability that allows users to redeem any coupon in the system, regardless of ownership. The method uses `Coupon.find_by(code: @coupon_code)` which searches all coupons globally, enabling users to exploit other users' personal coupon codes and potentially cause significant financial losses.

## Key Points to Mention

1. **Vulnerable Code Location**: The `find_coupon` private method on line with `Coupon.find_by(code: @coupon_code)` performs an unscoped database query that ignores coupon ownership
2. **Authorization Bypass**: The current implementation completely bypasses user authorization checks, allowing any authenticated user to use coupons that belong to other users
3. **Correct Implementation**: Should be `current_user.coupons.find_by(code: @coupon_code)` or `@user.coupons.find_by(code: @coupon_code)` to scope the search to only the current user's coupons
4. **Business Impact**: This vulnerability could lead to unauthorized discount usage, revenue loss, and potential abuse where users share or steal coupon codes meant for specific individuals
5. **Missing Validation**: Despite having other comprehensive coupon validations (expiration, usage limits, minimum amounts), the fundamental ownership check is completely absent

## Severity Rationale

• **High Financial Risk**: Users can potentially use high-value promotional coupons intended for other customers, leading to direct revenue loss and discount abuse
• **System-Wide Vulnerability**: Every coupon redemption is affected since the authorization check is missing entirely, making this a pervasive security issue rather than an edge case
• **Business Logic Violation**: Completely undermines the coupon system's intended user-specific distribution model, potentially making targeted marketing campaigns and loyalty programs ineffective

## Acceptable Variations

• May be described as "horizontal privilege escalation" or "insecure direct object reference (IDOR)" in addition to authorization bypass terminology
• Could focus on the missing scoping/filtering by user relationship rather than framing it specifically as an authorization issue
• Might suggest alternative implementations like adding a separate authorization check method or using policy objects, as long as the core fix ensures user-scoped coupon lookup