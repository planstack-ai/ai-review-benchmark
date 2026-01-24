# Column Default Null Management System

## Overview

The system needs to manage database column defaults appropriately, ensuring that columns have sensible default values rather than defaulting to NULL unnecessarily. This is critical for data integrity, application reliability, and preventing unexpected null pointer exceptions. The system should distinguish between columns that legitimately need to allow NULL values versus those that should have meaningful defaults.

## Requirements

1. All string/text columns must have empty string ('') as default instead of NULL unless explicitly designed to differentiate between "empty" and "unknown" states
2. All numeric columns must have zero (0) as default instead of NULL unless the business logic requires distinguishing between "zero" and "not set"
3. All boolean columns must have an explicit default value (true or false) and never default to NULL
4. All timestamp columns for tracking purposes (created_at, updated_at, etc.) must have appropriate default values
5. Foreign key columns may remain NULL by default only when representing optional relationships
6. Enum columns must have a sensible default value from the available enum options
7. The system must validate that no critical business logic columns are left with NULL defaults during migration creation
8. Default values must be set at the database level, not just in application code

## Constraints

1. Existing data must be preserved when adding default values to existing columns
2. Default values must be compatible with the column's data type and constraints
3. Default values should not conflict with existing validation rules
4. Changes to column defaults must be reversible through database migrations
5. Default values must be consistent across different database engines (PostgreSQL, MySQL, SQLite)

## References

See context.md for examples of existing column default implementations and patterns used throughout the codebase.