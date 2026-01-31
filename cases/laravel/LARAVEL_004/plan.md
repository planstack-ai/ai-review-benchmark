# Laravel Middleware Authentication and Authorization Order

## Overview

This application requires proper middleware ordering to ensure secure access control. The system must authenticate users before attempting to authorize their access to protected resources. This is a critical security pattern where the identity of the user must be established before checking their permissions.

## Requirements

1. Authentication middleware must be applied before authorization middleware in the middleware stack
2. The application must verify user identity through authentication before checking user permissions
3. Unauthenticated requests must be handled appropriately before any authorization checks occur
4. The middleware order must ensure that authorization logic only runs on authenticated users
5. Protected routes must have both authentication and authorization middleware applied in the correct sequence
6. The system must prevent authorization checks from running on unauthenticated requests

## Constraints

1. Authentication middleware must complete successfully before authorization middleware executes
2. If authentication fails, the request must not proceed to authorization middleware
3. Authorization middleware must assume that authentication has already been verified
4. The middleware chain must be configured to handle authentication failures gracefully
5. No authorization logic should execute for anonymous or unauthenticated users

## References

See context.md for existing middleware implementations and route configurations that demonstrate the current setup.