# Performance-Critical Raw SQL Query Implementation

## Overview

The application requires a high-performance analytics dashboard that displays complex aggregated data from multiple tables. Due to the complexity of the required joins, subqueries, and aggregations, standard ORM methods would generate inefficient queries that could impact system performance. This feature implements intentional raw SQL queries to achieve optimal database performance for time-sensitive reporting requirements.

## Requirements

1. Implement a method that executes raw SQL queries for complex data aggregation across multiple related tables
2. The raw SQL must include proper parameter binding to prevent SQL injection vulnerabilities
3. Query results must be returned in a structured format suitable for dashboard consumption
4. The implementation must include appropriate error handling for database connection issues
5. Raw SQL queries must be documented with comments explaining their performance necessity
6. The method must accept dynamic parameters for filtering data by date ranges and user segments
7. Query execution time must be logged for performance monitoring purposes
8. Results must be cached appropriately to reduce database load for repeated requests

## Constraints

1. Raw SQL usage must be justified by performance requirements that cannot be met through ORM
2. All user inputs passed to raw queries must be properly sanitized and parameterized
3. Query complexity must warrant the maintenance overhead of raw SQL over ORM alternatives
4. Database-specific SQL features may be used if they provide significant performance benefits
5. Raw queries must be compatible with the application's primary database engine

## References

See context.md for existing database schema, related model implementations, and performance benchmarking data that supports the decision to use raw SQL for this specific use case.