# FP_011: Intentional No Index

## Overview

Implement a boolean column used in queries **without** an index. This is a **CORRECT** implementation that may appear to be a performance issue to reviewers who expect all queried columns to be indexed.

## Requirements

- Store user email verification status as boolean
- Query users by verification status
- Intentionally avoid indexing the boolean column
- Document why indexing would hurt performance

## Why This Looks Suspicious But Is Correct

### What Looks Wrong

1. Boolean column `email_verified` used in WHERE clauses
2. No index on `email_verified` column
3. Query methods that filter by verification status
4. Apparent full table scan on every query

### Why It's Actually Correct

1. **Low cardinality**: Boolean columns have only 2 possible values
2. **Uniform distribution**: ~50% verified, ~50% unverified (not selective enough)
3. **Index overhead**: Maintaining index costs more than table scan benefit
4. **Small selectivity benefit**: Index would eliminate only ~50% of rows
5. **Database optimizer behavior**: Most databases ignore low-cardinality indexes

### Index Decision Criteria

**When NOT to index (this case):**
- Cardinality < 5% of row count (boolean = 2 values only)
- Query returns >10-20% of table rows
- High write volume (index maintenance cost)
- Small table size (<100k rows)

**When TO index:**
- High cardinality (many distinct values)
- Queries return <5% of rows
- Read-heavy workload
- Large table size (>1M rows)

### Performance Analysis

For a table with 100,000 users (50% verified):

**With index:**
- Index scan: ~50,000 row IDs
- Table lookups: ~50,000 rows
- Index maintenance: CPU cost on every INSERT/UPDATE
- Storage: Additional index space

**Without index:**
- Sequential scan: 100,000 rows (but in-memory, cache-friendly)
- No index maintenance overhead
- Better write performance

**Verdict**: Table scan is actually faster for this use case.
