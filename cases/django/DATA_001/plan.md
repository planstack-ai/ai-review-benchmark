# Django Data Integrity Without Foreign Key Constraints

## Overview

This system manages product categories and products where products reference categories by ID, but without using Django's built-in foreign key constraints. The application must maintain referential integrity manually to ensure data consistency when categories are deleted or modified, while still allowing flexible data relationships.

## Requirements

1. Create a Category model with fields for name and description
2. Create a Product model that references categories using an integer category_id field (not a ForeignKey)
3. Implement manual referential integrity checks before category deletion
4. Prevent deletion of categories that have associated products
5. Provide a method to safely delete categories by first handling dependent products
6. Include validation to ensure category_id references exist when creating/updating products
7. Implement a method to find orphaned products (products with invalid category_id references)
8. Create admin interface integration for both models
9. Add appropriate string representations for both models
10. Include model methods to retrieve related objects manually

## Constraints

1. Must not use Django's ForeignKey field type for the category relationship
2. Category deletion must be prevented if any products reference that category
3. Product creation/update must validate that the referenced category exists
4. System must handle cases where category_id references become invalid
5. All referential integrity checks must be implemented in model methods or custom managers
6. Admin interface must display meaningful information about relationships

## References

See context.md for existing model patterns and database relationship examples in the current codebase.