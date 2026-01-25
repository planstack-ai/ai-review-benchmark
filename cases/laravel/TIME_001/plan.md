# Flash Sale Scheduling

## Overview

Schedule and manage time-limited flash sales.

## Requirements

1. Sales have start and end times
2. Products only available at sale price during active sale
3. Handle timezone correctly (all times stored in UTC)
4. Sale applies based on server time, not user's local time

## Business Rules

- Sale is active when: start_time <= current_time < end_time
- All times stored and compared in UTC
- User sees times converted to their timezone for display only
