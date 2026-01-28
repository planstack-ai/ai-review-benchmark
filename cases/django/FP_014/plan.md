# User Status Tracking System

## Overview

This system manages user status information for a web application where users can have one of several predefined status values (active, inactive, pending, suspended). The status field is designed to have low cardinality with only a few possible values, making it suitable for scenarios where a database index may not provide significant performance benefits due to the limited number of distinct values.

## Requirements

1. Create a Django model to represent user status information with a status field that can contain one of four possible values: "active", "inactive", "pending", or "suspended"

2. Implement the status field as a character field with appropriate choices to ensure data integrity

3. Include a created timestamp field to track when the status record was created

4. Include an updated timestamp field that automatically updates when the record is modified

5. Provide a string representation method that displays meaningful information about the status record

6. Ensure the model follows Django naming conventions and best practices

7. The status field should be designed without a database index, as the low cardinality nature of the field (only 4 possible values) makes indexing potentially inefficient

8. Include proper field validation through Django's choices mechanism

## Constraints

1. Status values must be limited to exactly four options: "active", "inactive", "pending", "suspended"

2. The status field must not accept null values

3. The status field must have a reasonable maximum length to accommodate the longest status value

4. Timestamp fields should automatically handle creation and update times

5. The model should be suitable for use in Django admin interface

## References

See context.md for information about existing codebase patterns and related implementations.