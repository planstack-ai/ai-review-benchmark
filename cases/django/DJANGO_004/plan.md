# Django User Welcome Email Signal Implementation

## Overview

The application needs to send a welcome email to users when they are first created in the system. This functionality should be implemented using Django signals to maintain loose coupling between the user creation process and the email notification system. The welcome email should only be sent once per user, specifically when a new user account is initially created, not on subsequent updates to the user record.

## Requirements

1. Implement a Django signal handler that triggers when a User model instance is saved
2. The signal handler must only send welcome emails for newly created users
3. The signal handler must not send welcome emails when existing users are updated
4. The welcome email functionality must be triggered automatically without manual intervention
5. The signal handler must be properly connected to the User model's save operations
6. The email sending logic must be contained within the signal handler function
7. The signal handler must be registered and active when the Django application starts

## Constraints

1. Welcome emails must not be sent multiple times to the same user
2. The signal handler must not interfere with normal user creation or update operations
3. The implementation must use Django's built-in signal system
4. The signal handler must not cause user save operations to fail if email sending encounters errors
5. The signal must only respond to User model instances, not other model types

## References

See context.md for existing codebase structure and related implementations.