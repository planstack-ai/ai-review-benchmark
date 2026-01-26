# Audit Logging Service

## Overview

Comprehensive audit logging for security and compliance.

## Requirements

1. Log all significant actions (CRUD operations, login events)
2. Include user and context information (IP address, user agent)
3. Record entity changes with old and new values
4. Handle sensitive data appropriately (redact passwords, tokens, etc.)

## Notes

- Sensitive fields are sanitized at the top level
- Login attempts capture success/failure status
