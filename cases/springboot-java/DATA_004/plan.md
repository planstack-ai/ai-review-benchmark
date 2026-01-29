# Product Search with Soft Delete

## Overview

Products use soft delete to maintain historical data for orders. Deleted products should not appear in search results or product listings.

## Requirements

1. Products can be soft-deleted (marked as deleted)
2. Deleted products should not appear in search results
3. Deleted products should not be purchasable
4. Historical order data must still reference deleted products
5. Admin can view deleted products separately

## Constraints

1. Normal queries must exclude deleted records by default
2. Soft delete must be consistent across all query methods
3. Performance should not be significantly impacted
4. Must work with derived query methods and custom queries

## References

See context.md for soft delete pattern.
