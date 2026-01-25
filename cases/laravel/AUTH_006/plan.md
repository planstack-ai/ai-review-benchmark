# Points Access Service

## Overview

The system provides API access to user loyalty points data. Users can view their point balance, transaction history, and summaries. This is sensitive personal financial data requiring proper authorization.

## Requirements

1. Authenticate user before any points access
2. Show points balance and totals
3. List points with pagination
4. Generate points summary with category breakdown
5. Show recent activity (last 30 days)
6. **Users can only access their own points data**
7. Support different viewing modes (show, list, summary)

## Constraints

1. User must be logged in
2. User can only view their own points, not other users'
3. User ID parameter should be ignored or validated against current user
4. Paginate results with max 100 per page

## References

See context.md for Points model and user relationship structure.
