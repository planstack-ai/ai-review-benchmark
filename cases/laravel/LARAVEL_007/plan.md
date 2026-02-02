# Email Notification Service with Proper Test Isolation

## Overview

The system needs to send email notifications when users complete specific actions. The email sending functionality must be thoroughly tested to ensure reliability, with proper test isolation to prevent interference between test cases and avoid actual email delivery during testing.

## Requirements

1. Create an email notification service that sends emails when users perform designated actions
2. Implement proper email sending functionality using Laravel's Mail facade
3. Create comprehensive test coverage for the email sending functionality
4. Ensure tests use mocking to prevent actual email delivery during test execution
5. Implement proper test isolation so that each test case runs independently
6. Verify that mocked email functionality is properly reset between test cases
7. Test cases must validate that emails are sent with correct recipients and content
8. Include both positive test cases (emails should be sent) and negative test cases (emails should not be sent)
9. Ensure test suite can run multiple times consecutively without interference
10. Implement proper cleanup mechanisms to maintain test environment integrity

## Constraints

1. Tests must not send actual emails to real email addresses
2. Each test case must start with a clean state regardless of previous test execution
3. Mock configurations from one test must not affect subsequent tests
4. Test execution order must not impact test results
5. All email-related assertions must work consistently across multiple test runs

## References

See context.md for existing codebase structure and testing patterns to follow.