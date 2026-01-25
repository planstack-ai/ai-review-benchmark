# Subscription Billing Cycle

## Overview

Calculate billing periods and proration for subscriptions.

## Requirements

1. Bill on same day each month
2. Handle month-end edge cases (Jan 31 → Feb 28)
3. Calculate proration for mid-cycle changes
4. Track billing period start/end dates

## Business Rules

- Monthly subscriptions bill on the same date each month
- If original date doesn't exist (e.g., 31st), use last day of month
- Proration calculated as: (days_remaining / days_in_period) * price
