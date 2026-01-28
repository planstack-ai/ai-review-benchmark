# Django Performance Optimization: Efficient Count Queries

## Overview

The application needs to display statistical information about database records, including total counts of various entities. Currently, the system may be using inefficient methods to count records, such as loading all objects into memory and using Python's `len()` function. This creates unnecessary memory overhead and poor performance, especially with large datasets. The system should leverage database-level COUNT operations to efficiently retrieve totals without loading actual record data.

## Requirements

1. All count operations must use database-level COUNT queries rather than loading objects into memory
2. Count queries must not fetch actual record data, only the count value
3. The system must provide accurate counts for filtered datasets when applicable
4. Count operations must work correctly with Django QuerySet filtering and exclude operations
5. The implementation must handle empty result sets gracefully, returning 0 for no matches
6. Count queries must be executed as single database operations, not multiple queries
7. The system must maintain consistent count accuracy across different model relationships
8. Count operations must be compatible with Django's ORM query optimization features

## Constraints

1. Count operations must not cause N+1 query problems
2. The implementation must not load unnecessary data into application memory
3. Count queries must respect existing model permissions and access controls
4. The system must handle database connection errors gracefully during count operations
5. Count operations must work correctly with both simple and complex QuerySet filters
6. The implementation must not break existing functionality that depends on count results

## References

See context.md for existing codebase structure and current implementation patterns.