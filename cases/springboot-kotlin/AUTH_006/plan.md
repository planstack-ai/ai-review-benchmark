# User Points API Service

## Overview

This service implements an API endpoint for users to view their loyalty points balance. Users should only be able to access their own points information, not other users' points.

## Requirements

1. Create an API endpoint to retrieve user points balance
2. Users can only view their own points
3. Return points balance and recent transaction history
4. Include points expiration information
5. Handle unauthorized access attempts gracefully
6. Log all points inquiries for auditing
7. Support pagination for transaction history
8. Return appropriate error responses for invalid requests

## Constraints

1. Users must be authenticated to access points
2. Users cannot view other users' points
3. Points data is sensitive and must be protected
4. API must validate user identity against requested data
5. The service should be stateless and thread-safe
6. Rate limiting should be applied to prevent abuse

## References

See context.md for existing user authentication and points management patterns in the codebase.
