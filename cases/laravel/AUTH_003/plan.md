# Order Report Generation System

## Overview

The system generates sales reports including order statistics, revenue calculations, and customer analytics. Reports can be filtered by date range and status. The system must respect user data privacy by excluding deleted users' data.

## Requirements

1. Generate summary reports with total orders and revenue
2. Group orders by status for analysis
3. Identify top customers by spending
4. Calculate average order value
5. Export orders to CSV format
6. Support date range and status filtering
7. **Exclude data from deleted/soft-deleted users**
8. Paginate results for large datasets

## Constraints

1. Reports should only include data from active users
2. Deleted users' orders should not appear in reports (GDPR compliance)
3. Customer personal data (email) from deleted accounts must not be exposed
4. Performance should be optimized for large datasets

## References

See context.md for User soft delete implementation and order relationships.
