# Performance-Critical Analytics Dashboard Query Implementation

## Overview

The analytics dashboard requires a complex aggregation query that joins multiple tables with custom calculations, date range filtering, and performance optimizations. Due to the complexity of the required SQL operations and performance requirements for large datasets, this feature necessitates the use of raw SQL queries rather than Django ORM to achieve acceptable response times.

## Requirements

1. Implement a dashboard analytics endpoint that retrieves sales performance metrics across multiple dimensions
2. Query must aggregate data from orders, products, customers, and sales_representatives tables
3. Include custom calculations for commission rates, profit margins, and performance rankings
4. Support date range filtering with optimized index usage
5. Return results grouped by sales representative with subtotals and rankings
6. Implement proper parameterized queries to prevent SQL injection
7. Handle database connection management appropriately
8. Include error handling for database connectivity issues
9. Return structured data suitable for JSON serialization
10. Achieve query execution time under 500ms for datasets up to 100,000 records

## Constraints

1. Date range parameters must be validated before query execution
2. Results must be limited to a maximum of 1000 records to prevent memory issues
3. Only active sales representatives should be included in results
4. Commission calculations must handle null values appropriately
5. Database queries must use read-only database connections where available
6. Query results must maintain consistent ordering across multiple executions

## References

See context.md for existing database schema, model definitions, and related query patterns used elsewhere in the application.