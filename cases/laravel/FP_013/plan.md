# Bulk Product Price Update System

## Overview

The system needs to perform bulk price updates on products during promotional campaigns or market adjustments. These updates should bypass individual model callbacks and validations to ensure optimal performance when processing large datasets. The feature is designed for administrative batch operations where standard model lifecycle events would create unnecessary overhead and potential performance bottlenecks.

## Requirements

1. Implement a bulk update mechanism that can modify multiple product prices simultaneously
2. The update operation must bypass ActiveRecord callbacks and validations for performance optimization
3. Support updating prices based on percentage adjustments or fixed amount changes
4. Process updates in batches to handle large product catalogs efficiently
5. Provide logging of the bulk update operation including affected record count
6. Include basic error handling for database-level constraints
7. Return summary information about the update operation (records affected, execution time)
8. Support filtering products by category or other criteria before applying updates
9. Ensure the operation is atomic - either all updates succeed or none are applied
10. Implement appropriate authorization checks before allowing bulk updates

## Constraints

1. Updates must only affect products with active status
2. Price values cannot be negative after updates
3. Percentage adjustments must be within reasonable bounds (-90% to +500%)
4. Batch size should not exceed 1000 records per operation
5. Operation must complete within reasonable time limits for web requests
6. Database connection timeouts must be handled gracefully
7. Concurrent bulk update operations should be prevented or queued

## References

See context.md for existing product model structure and current update patterns used in the application.