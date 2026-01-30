# User Registration Entity

## Overview

Define the User entity for user registration. Email addresses must be unique across the system to prevent duplicate accounts.

## Requirements

1. Each user must have a unique email address
2. Registration should fail if email already exists
3. Database must enforce uniqueness constraint
4. Support case-insensitive email uniqueness

## Constraints

1. No two users can have the same email
2. Uniqueness must be enforced at database level
3. Application should handle constraint violations gracefully

## References

See context.md for existing schema.
