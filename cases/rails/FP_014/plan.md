# Code Review Benchmark Service

## Overview

The system needs a service to run automated code quality benchmarks on repository files. The service analyzes code files using different benchmark types (performance, security, maintainability) and stores the results for reporting purposes.

## Requirements

1. Accept a repository ID and benchmark type as input parameters
2. Validate benchmark type against allowed values (performance, security, maintainability)
3. Process all active code files in the repository that are under 1MB in size
4. Use batch processing (find_each) to handle large numbers of files efficiently
5. Analyze each file using the appropriate analyzer based on benchmark type
6. Calculate aggregate metrics (total score, average score, issue count)
7. Store benchmark results atomically in the database
8. Generate reports from stored benchmark data
9. Return success/failure results with appropriate messages

## Constraints

1. Only process files marked as active and under 1MB
2. Benchmark results must be stored atomically (all or nothing)
3. Use find_each for database cursor-based iteration to avoid loading all DB records at once
4. Results may be accumulated in memory for aggregate metric calculation (acceptable for typical repository sizes)
5. Validate repository existence before processing
6. Default to 'performance' benchmark type if invalid type provided
7. Report generation should only include data from the last 30 days
8. Individual INSERT statements are acceptable for data integrity (callbacks, validations)
9. Report aggregates cumulative metrics across all benchmark runs (intended for trend analysis)
10. Report generation is admin-only; loading full result set is acceptable for accuracy

## References

See context.md for Repository, CodeFile, Benchmark, and BenchmarkResult model definitions.
