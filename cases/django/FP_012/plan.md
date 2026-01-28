# Performance-Critical Analytics Dashboard with Complex Raw SQL Queries

## Overview

The system needs to generate real-time analytics for an e-commerce platform's executive dashboard. The dashboard displays complex metrics including customer lifetime value, product performance across categories, and sales trends with geographic breakdowns. Due to the complexity of the calculations and the need for sub-second response times, raw SQL queries with multiple joins and aggregations are required to meet performance requirements that cannot be achieved through Django ORM.

## Requirements

1. Implement a dashboard view that executes raw SQL queries to calculate customer lifetime value across different time periods
2. Create raw SQL queries that join customer, order, product, and geographic data tables with proper indexing considerations
3. Generate aggregated sales metrics by product category with year-over-year comparisons using window functions
4. Implement geographic sales distribution analysis using raw SQL with spatial joins if applicable
5. Ensure all raw SQL queries use parameterized inputs to prevent SQL injection while maintaining performance
6. Cache query results appropriately to balance real-time data needs with performance requirements
7. Handle database connection pooling and query timeout scenarios gracefully
8. Provide fallback mechanisms when complex queries exceed acceptable response times
9. Log query execution times and performance metrics for monitoring purposes
10. Structure the code to allow for easy modification of SQL queries without changing core application logic

## Constraints

- Query response time must not exceed 2 seconds for any dashboard metric
- All user inputs must be properly sanitized and parameterized in raw SQL queries
- Database queries must be compatible with PostgreSQL-specific features and syntax
- The system must handle concurrent dashboard requests from up to 50 executive users
- Raw SQL queries must include appropriate error handling for database connectivity issues
- All monetary calculations must maintain precision to avoid rounding errors in financial reporting

## References

See context.md for existing database schema, model relationships, and current ORM-based implementations that need to be replaced with raw SQL for performance optimization.