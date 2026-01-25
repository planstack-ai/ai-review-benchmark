# Expected Critique

## Essential Finding

The report service includes orders from users who have been soft-deleted, violating privacy requirements. The `orders()` method queries all orders without filtering out those belonging to deleted users, exposing their personal data (email) and order history.

## Key Points to Mention

1. **Bug Location**: The `orders()` method uses `Order::with(['user', 'orderItems'])` without filtering for active users.

2. **Privacy Violation**: Deleted users have requested their data be removed, but their order history and email addresses still appear in reports.

3. **Correct Implementation**: Add a scope to exclude deleted users: `Order::whereHas('user', fn($q) => $q->whereNull('deleted_at'))`

4. **GDPR/Compliance Risk**: Data protection regulations require honoring deletion requests. Including deleted users' data in reports violates the right to be forgotten.

5. **Data Exposure**: The `findTopCustomers` and CSV export methods expose deleted users' email addresses, which is particularly problematic.

## Severity Rationale

- **Legal Compliance**: GDPR and similar regulations require complete data erasure upon user request. This implementation fails to honor that.

- **Privacy Breach**: Deleted users' personal information (email, purchase history) remains exposed to staff viewing reports.

- **Trust Violation**: Users who delete their accounts expect their data to be removed from all systems and reports.

## Acceptable Variations

- **Different Fix Approaches**: Reviews might suggest using global scopes, a dedicated "active orders" scope, or middleware filtering.

- **Terminology Variations**: The bug might be described as "soft delete not respected," "GDPR violation," "data retention issue," or "incomplete user deletion."

- **Impact Descriptions**: Reviews might focus on "privacy compliance," "right to be forgotten," or "data protection failure."
