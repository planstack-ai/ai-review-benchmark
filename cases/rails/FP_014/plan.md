# Intentional No Index on Low Cardinality Status Column

## Overview

The application needs to track user account status using a status column that will have very few distinct values (active, inactive, suspended). Due to the low cardinality nature of this column and the specific query patterns in the application, an index on this column would provide minimal performance benefit while consuming unnecessary storage space and maintenance overhead.

## Requirements

1. Create a users table with a status column that stores account status information
2. The status column must support exactly three possible values: 'active', 'inactive', and 'suspended'
3. The status column must have a default value of 'active' for new user registrations
4. The status column must not be null and must be validated at the application level
5. The status column must be implemented as a string/varchar type to maintain readability
6. No database index should be created on the status column due to its low cardinality
7. The table must include standard user identification fields (id, email, name)
8. The table must include timestamp fields for record tracking (created_at, updated_at)

## Constraints

1. The status column must reject any values other than the three specified options
2. All users must have exactly one status at any given time
3. The status field must be easily readable in database queries without requiring lookups
4. The implementation must not include any database-level indexes on the status column
5. Status changes must be tracked through the updated_at timestamp

## References

See context.md for examples of similar low cardinality column implementations and indexing decisions in the existing codebase.