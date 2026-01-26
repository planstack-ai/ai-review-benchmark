# Analytics Event Query Service

## Overview

A service to query analytics event data for reporting and dashboard purposes. Due to performance requirements for aggregating large datasets, the service uses raw SQL queries with proper parameterization.

## Requirements

1. Implement methods to retrieve event counts grouped by date and event type
2. Provide an event type summary with unique user and session counts
3. Implement a user activity summary with overall metrics for a date range
4. Create a conversion funnel showing user progression through event types
5. Use parameterized SQL queries to prevent SQL injection
6. Include proper error handling for database connectivity issues
7. Validate date range parameters before query execution
8. Limit results to prevent memory issues with large datasets

## Constraints

1. Date range parameters must be validated (start_date must be before end_date)
2. Results must be limited to a maximum of 1000 records
3. All user inputs must be passed through parameterized queries
4. Database errors must be caught and re-raised with descriptive messages

## References

See context.md for existing database schema and model definitions.
