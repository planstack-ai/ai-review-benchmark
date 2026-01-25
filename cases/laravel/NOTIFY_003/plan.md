# Password Reset Email

## Overview

Send password reset emails with secure tokens.

## Requirements

1. Generate secure reset token
2. Send email with reset link
3. Token expires after 1 hour
4. Invalidate previous tokens on new request

## Security Rules

- Token must be cryptographically secure
- Don't reveal if email exists in system
- Log all reset attempts
