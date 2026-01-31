# Add Priority Column to Orders Table

## Overview

The orders management system needs to track order priority levels to enable better order processing workflows. A new priority column should be added to the orders table to store integer values representing different priority levels, where higher numbers indicate higher priority.

## Requirements

1. Add a new column named `priority` to the existing `orders` table
2. The column must store integer values
3. The column must allow NULL values by default
4. The column should be added without affecting existing order records
5. The migration must be reversible (include a rollback method)
6. The migration should follow Rails naming conventions for database migrations
7. The column should be positioned appropriately within the table structure

## Constraints

1. Existing order records must remain unchanged and functional after the migration
2. The migration must not cause data loss or corruption
3. The column must accept standard integer values within the database's integer range
4. NULL values should be explicitly allowed to maintain backward compatibility
5. The migration file must follow Rails timestamp naming convention

## References

See context.md for existing database schema and migration patterns used in this codebase.