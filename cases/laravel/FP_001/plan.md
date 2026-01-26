# User Profile Management Service

## Overview

A user profile management service that provides CRUD operations on user profiles with email validation and logging.

## Requirements

1. Support creation, update, and deletion of user profiles
2. Validate email format and uniqueness
3. Send welcome email on user creation
4. Log user operations (create, update, delete)
5. Support user activation and deactivation
6. Allow finding users by email

## Constraints

1. Email addresses must be unique
2. Only allow specific fields to be mass-assigned (first_name, last_name, email, phone, role)
3. Cascade delete associated data via foreign keys

## Notes

- Posts and comments are cascade deleted via foreign keys in the database schema
- Error collection is optional and may be empty if model doesn't have validation errors
