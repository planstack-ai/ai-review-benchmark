# Email Notification Recipient Verification System

## Overview

The system needs to send email notifications to users while ensuring that each email reaches the correct intended recipient. This is critical for maintaining user privacy and preventing sensitive information from being sent to wrong email addresses. The notification system should handle various types of email communications including account updates, password resets, and general notifications while maintaining strict recipient verification.

## Requirements

1. The system must verify the recipient email address before sending any notification
2. Each notification must be associated with exactly one intended recipient user
3. The system must validate that the recipient email matches the user's current email address in the database
4. Email notifications must include proper recipient validation in the sending process
5. The system must log successful email deliveries with recipient information
6. Failed email deliveries must be logged with error details and recipient information
7. The notification system must support different types of email notifications (welcome, password reset, account updates)
8. Each email must contain a unique identifier linking it to the specific recipient
9. The system must prevent sending emails to deactivated or suspended user accounts
10. Email templates must be populated with the correct recipient's personal information

## Constraints

- Email addresses must be validated for proper format before sending
- Users with unverified email addresses should not receive certain types of notifications
- The system must not send duplicate notifications to the same recipient within a 5-minute window
- Email sending must fail gracefully if recipient validation fails
- All email operations must be logged for audit purposes
- The system must handle cases where a user's email address has been recently updated
- Notification preferences must be respected for each recipient

## References

See context.md for existing user management and email service implementations that should be integrated with this notification system.