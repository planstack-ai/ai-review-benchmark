# Order Route Model Binding Implementation

## Overview

The application needs to implement route model binding for order resources using UUID-based identification. Orders are identified by their UUID field rather than auto-incrementing IDs, and the routing system must properly resolve order instances from URL parameters. This feature enables clean, RESTful URLs while maintaining UUID-based identification for enhanced security and scalability.

## Requirements

1. Configure route model binding to resolve Order models using the UUID field instead of the default ID field
2. Define routes that accept UUID parameters for order-related endpoints
3. Ensure the Order model has proper UUID field configuration and database schema
4. Implement automatic model resolution so that route handlers receive fully hydrated Order instances
5. Handle cases where the provided UUID does not match any existing order record
6. Maintain RESTful URL patterns with UUID parameters (e.g., `/orders/{order}` where `{order}` is a UUID)
7. Ensure the binding works for all HTTP methods (GET, POST, PUT, PATCH, DELETE)
8. Configure the route key name to use the UUID field for model resolution

## Constraints

1. UUIDs must be valid RFC 4122 format
2. Route model binding must fail gracefully with 404 responses for non-existent UUIDs
3. The UUID field must be unique and indexed in the database
4. Route parameters must maintain semantic meaning (use `{order}` not `{uuid}`)
5. Existing order records must have valid UUIDs populated
6. The implementation must not break existing functionality or other model bindings

## References

See context.md for existing Order model structure, database migrations, and current routing configuration.