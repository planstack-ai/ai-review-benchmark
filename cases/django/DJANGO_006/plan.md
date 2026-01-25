# User Profile Management with Authentication Requirements

## Overview

The application provides user profile management functionality where authenticated users can view and update their personal profile information. This feature is part of a web application that handles sensitive user data and requires proper access control to ensure users can only access their own profile information and that unauthenticated users cannot access any profile data.

## Requirements

1. All profile-related views must require user authentication before allowing access
2. Unauthenticated users attempting to access profile views must be redirected to the login page
3. The profile view must display the current user's profile information
4. The profile edit view must allow authenticated users to update their profile information
5. Profile views must only show data belonging to the currently authenticated user
6. The application must handle both GET and POST requests for profile management
7. Form validation must be implemented for profile updates
8. Success messages must be displayed after successful profile updates
9. The profile edit form must be pre-populated with existing user data
10. Navigation must include appropriate links to profile-related functionality

## Constraints

1. Anonymous users must not be able to access any profile information
2. Users must not be able to access or modify other users' profiles
3. All profile data modifications must be validated before saving
4. The login redirect must preserve the originally requested URL when possible
5. Profile updates must only modify the current user's data
6. Form submissions must include proper CSRF protection

## References

See context.md for existing codebase structure, models, and related implementations that this feature should integrate with.