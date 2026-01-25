# Daily Report Generation

## Overview

Generate daily sales reports at the end of each business day.

## Requirements

1. Aggregate sales for the previous business day
2. Run at midnight in business timezone
3. Handle date boundaries correctly
4. Store report with correct date reference

## Business Rules

- Report for "Jan 15" covers Jan 15 00:00:00 to Jan 15 23:59:59 in business timezone
- Business timezone: America/New_York
- Server runs in UTC
