## Usage Guidelines

The `Product.active` scope is the **canonical way** to filter active products throughout the application. This ensures:
- Consistent behavior when the definition of "active" changes
- DRY principle compliance
- Better maintainability

All queries for active products should use `Product.active` rather than `Product.where(status: 'active')`.
