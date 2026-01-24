# Performance-Critical Analytics Query System

## Overview

The system needs to generate complex analytics reports for large datasets where ActiveRecord's query interface would be insufficient for performance requirements. The application processes millions of records and requires optimized SQL queries with custom aggregations, window functions, and complex joins that cannot be efficiently expressed through Rails' ORM layer.

## Requirements

1. Implement a method that executes raw SQL queries for analytics report generation
2. The method must accept dynamic parameters for date ranges and filtering criteria
3. Query results must be returned as structured data suitable for report rendering
4. The implementation must handle multiple complex aggregations in a single query
5. Support for window functions and advanced SQL features not available in ActiveRecord
6. Query execution time must be optimized for large dataset processing
7. The method must properly sanitize and parameterize user inputs
8. Results must include proper column naming and data type handling
9. The implementation must support multiple database-specific optimizations
10. Error handling must distinguish between SQL syntax errors and data issues

## Constraints

1. Raw SQL usage is justified only for performance-critical operations
2. All user inputs must be properly parameterized to prevent SQL injection
3. Query complexity requires database-specific optimization features
4. The operation processes datasets too large for ActiveRecord's memory footprint
5. Response time requirements cannot be met with ORM-generated queries
6. The query involves multiple tables with complex join conditions
7. Custom aggregation functions are required that are not supported by ActiveRecord

## References

See context.md for existing database schema, performance requirements, and related analytics infrastructure implementations.