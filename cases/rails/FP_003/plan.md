# User Profile Management System

## Overview

A user profile management system that allows users to maintain personal profiles with associated contact information. The system needs to support basic CRUD operations for user profiles and their related contact details, enabling users to manage their personal information effectively.

## Requirements

1. Create a User model that can store basic user information including name and email
2. Create a Profile model that belongs to a User and stores additional user details
3. Establish a one-to-one association between User and Profile models
4. Create a Contact model that belongs to a User for storing contact information
5. Establish a one-to-many association between User and Contact models
6. Implement standard ActiveRecord association methods for navigating between related models
7. Support creation, reading, updating, and deletion of users and their associated data
8. Ensure proper foreign key relationships are established in the database schema
9. Allow users to have multiple contact entries (phone, email, address, etc.)
10. Maintain referential integrity between associated models

## Constraints

1. Each user must have a unique email address
2. A profile can only belong to one user
3. Contact information must be associated with an existing user
4. User deletion should handle associated profile and contact cleanup appropriately
5. All models should follow Rails naming conventions
6. Database migrations must include proper indexing for foreign keys

## References

See context.md for existing model implementations and database schema examples.