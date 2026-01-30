# Intentional No Index on Low Cardinality Column

## Overview

This test case demonstrates a scenario where a database column with low cardinality (few distinct values) intentionally does not have an index. The column stores status values with only a handful of possible states, making an index potentially unnecessary or even counterproductive for query performance. This represents a valid architectural decision that should not trigger false positive warnings from automated code review tools.

## Requirements

1. Create a database migration that adds a status column to an existing table
2. The status column must be of string or integer type with a limited set of possible values
3. The column must have low cardinality (typically 2-5 distinct values maximum)
4. The column must NOT have an index defined in the migration
5. The column should be used in model validations to restrict values to the allowed set
6. Include at least one query method that filters by the status column
7. The status values should represent common business states (e.g., active/inactive, pending/approved/rejected)
8. Ensure the column allows for efficient queries despite the lack of index due to low cardinality

## Constraints

1. The status column must not be nullable unless explicitly required by business logic
2. Status values must be validated at the application level
3. The column should not be part of a composite index requirement
4. Query patterns using this column should be simple equality checks
5. The table size should be reasonable for full table scans when filtering by status

## References

See context.md for examples of similar low cardinality column implementations and performance considerations for unindexed status fields.