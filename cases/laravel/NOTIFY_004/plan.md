# Subscription Renewal Reminder

## Overview

Send reminder emails before subscription expires.

## Requirements

1. Send reminder 7 days before expiration
2. Send final reminder 1 day before expiration
3. Track which reminders have been sent
4. Handle timezone for scheduling

## Reminder Rules

- First reminder: 7 days before current_period_end
- Final reminder: 1 day before current_period_end
- Don't send reminders for cancelled subscriptions
- Send at 9 AM in user's timezone
