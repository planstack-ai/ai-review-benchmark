# Django Model Column Default Null Handling

## Overview

This feature ensures that Django model fields have appropriate default values to prevent null constraint violations and provide sensible fallback behavior. When fields are marked as non-nullable but lack explicit default values, the system should automatically provide appropriate defaults based on the field type to maintain data integrity and prevent runtime errors during model operations.

## Requirements

1. All non-nullable CharField and TextField fields must have empty string ('') as the default value when no explicit default is provided
2. All non-nullable IntegerField, FloatField, and DecimalField fields must have zero (0) as the default value when no explicit default is provided
3. All non-nullable BooleanField fields must have False as the default value when no explicit default is provided
4. All non-nullable DateTimeField fields must use Django's timezone.now function as the default value when no explicit default is provided
5. Fields that explicitly allow null=True should not receive automatic default values
6. Fields that already have explicit default values should not be modified
7. The default value assignment must occur during model field initialization
8. Foreign key fields without explicit defaults should remain unchanged to preserve Django's standard behavior
9. The system must handle both model definition time and migration scenarios consistently
10. Default values must be appropriate for the field's data type and constraints

## Constraints

1. Default values must not conflict with field validators or constraints
2. DateTime defaults must be timezone-aware when USE_TZ is enabled
3. Numeric defaults must respect field-specific constraints (max_digits, decimal_places for DecimalField)
4. String defaults must respect max_length constraints
5. The solution must not interfere with Django's existing field inheritance mechanisms
6. Default values should not be applied to abstract model fields unless they are used in concrete models
7. The implementation must be compatible with Django's migration system

## References

See context.md for existing Django model field implementations and default value patterns used in the codebase.