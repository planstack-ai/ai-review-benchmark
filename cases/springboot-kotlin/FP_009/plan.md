# FP_009: Intentional Raw SQL

## Overview
Implement a sales analytics repository using native SQL queries for performance-critical operations. The queries use database-specific features (window functions, CTEs) that cannot be efficiently expressed in JPQL/HQL and require native SQL.

## Requirements
1. Generate sales reports with complex aggregations using window functions
2. Calculate running totals and ranking using database-specific features
3. Use native SQL with `@Query(nativeQuery = true)` for performance
4. Properly bind all parameters using Spring Data JPA parameter binding (`:paramName`)
5. Include clear documentation explaining why native SQL is necessary

## Performance Justification
- **Complex Aggregations**: Window functions perform significantly better than JPQL alternatives
- **Database-Specific Features**: PostgreSQL-specific functions not available in JPQL
- **Query Optimization**: Native SQL allows database-specific query hints and optimization
- **Benchmark Results**: 10x performance improvement over JPQL for complex reports

## Why This Looks Suspicious But Is Correct
- **Native SQL** appears dangerous and prone to SQL injection
- However, this uses **proper parameter binding** (`:paramName` syntax)
- Spring Data JPA **automatically sanitizes** bound parameters
- The complexity **requires database-specific features** unavailable in JPQL
- This is a **standard pattern** for performance-critical analytics queries

## Implementation Notes
- Use `@Query(nativeQuery = true)` annotation
- Always use named parameters (`:paramName`) for binding
- Never concatenate strings to build queries
- Document why native SQL is necessary
- Consider using database views if queries become too complex
