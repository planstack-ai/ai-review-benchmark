# Expected Critique

## Essential Finding

The OrderReportService exposes order data from deleted users through its base `orders` method, which fails to filter out orders belonging to soft-deleted users. This creates a significant privacy violation where deleted user information remains accessible through order reports, CSV exports, and customer analytics, contradicting the expectation that user deletion should hide their associated data.

## Key Points to Mention

1. **Base Query Issue**: The `orders` method on line 52 uses `Order.includes(:user, :order_items)` without filtering out orders from deleted users, making all subsequent report operations include deleted user data.

2. **Privacy Violation in Customer Data**: The `find_top_customers` method explicitly joins with users table and exposes email addresses, but doesn't exclude soft-deleted users, potentially leaking deleted user information in top customer reports.

3. **Correct Implementation**: The base `orders` method should use `Order.joins(:user).where(users: { deleted_at: nil }).includes(:user, :order_items)` to ensure only orders from active users are included in all report operations.

4. **Widespread Impact**: The bug affects all service methods including `generate_report`, `export_orders_csv`, and `recent_orders_summary`, meaning deleted user data leaks through multiple reporting channels and data exports.

5. **Cascading Data Exposure**: The CSV export and order summaries format and display user email addresses from deleted accounts, creating multiple vectors for exposing information that should be hidden.

## Severity Rationale

- **Privacy Compliance Risk**: Exposing deleted user data through reports violates user privacy expectations and potentially regulatory requirements around data deletion and user rights
- **Business-Wide Impact**: All reporting functionality is affected, meaning deleted user information is accessible through multiple channels including exports, analytics, and customer insights
- **Data Governance Failure**: The service undermines the organization's soft-delete user mechanism by making deleted user data readily available through standard business operations

## Acceptable Variations

- **Alternative Filtering Approaches**: Reviews might suggest using scopes, model-level default filters, or application-level authorization checks instead of the specific joins/where clause, as long as they achieve the same filtering result
- **Different Terminology**: References to "soft-deleted users," "deactivated accounts," or "removed users" would be acceptable ways to describe users with non-null `deleted_at` timestamps
- **Broader Privacy Concerns**: Reviews might frame this as a GDPR compliance issue, data retention policy violation, or general authorization bypass, all of which accurately describe the core problem