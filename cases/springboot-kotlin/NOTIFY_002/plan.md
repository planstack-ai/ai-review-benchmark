# Background Job Failure Handling System

## Overview

The system needs to process background jobs for sending promotional emails to customers. These jobs run asynchronously and may fail due to various reasons such as external email service unavailability, network issues, or invalid recipient data. The system must implement proper error handling to ensure that failures are properly tracked, logged, and escalated to administrators for investigation and remediation.

## Requirements

1. Process batch email sending jobs asynchronously in the background
2. Handle external email service failures gracefully
3. Log all email sending attempts with their success or failure status
4. Notify system administrators when critical email failures occur
5. Track failed email attempts in the notification logs table
6. Re-throw exceptions after logging to ensure Spring's retry mechanism can work
7. Provide detailed error context in logs including order ID and customer email
8. Ensure that background job failures are visible and not silently ignored
9. Implement proper exception handling for network timeouts and service errors
10. Use appropriate logging levels for different failure scenarios

## Constraints

1. Background jobs must not fail silently without any notification
2. Administrator notification is required for all email service failures
3. Error messages must include sufficient context for debugging
4. Failed jobs should be tracked in the database for audit purposes
5. System must differentiate between transient failures (retry) and permanent failures
6. Email service exceptions must be properly logged before re-throwing
7. All async operations must include try-catch blocks with proper error handling

## References

See context.md for existing database schema, entity definitions, and notification infrastructure.
