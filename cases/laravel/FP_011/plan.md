# Admin Data Import Tool with Intentional Validation Bypass

## Overview

This feature implements an internal administrative tool for bulk data import operations. The tool is designed for trusted admin users to quickly import large datasets without the overhead of standard validation rules that apply to regular user operations. This bypass is intentional and necessary for administrative efficiency in data migration and bulk operations scenarios.

## Requirements

1. Create an admin-only data import interface accessible through the admin panel
2. Implement bulk import functionality that accepts CSV or JSON data formats
3. Bypass standard model validations during the import process to allow administrative data correction
4. Restrict access to users with admin privileges only
5. Log all import operations with user identification and timestamp
6. Provide feedback on the number of records processed during import
7. Handle large datasets efficiently without timeout issues
8. Maintain data integrity through transaction wrapping of import operations
9. Allow import of records that may not pass standard business validation rules
10. Provide clear documentation that validation bypass is intentional for admin operations

## Constraints

1. Access must be restricted to authenticated admin users only
2. Import operations must be logged for audit purposes
3. Large imports should be processed in batches to prevent memory issues
4. Transaction rollback must be available if import fails partway through
5. The interface should clearly indicate that validation is bypassed
6. Import functionality should not be accessible through public API endpoints

## References

See context.md for existing admin authentication patterns and data import utilities used elsewhere in the application.