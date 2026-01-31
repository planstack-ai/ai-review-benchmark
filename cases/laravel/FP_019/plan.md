# User Activity Dashboard with Optimized Read Performance

## Overview

The system needs to provide a high-performance user activity dashboard that displays comprehensive user statistics and recent activities. Due to the read-heavy nature of dashboard queries and the need for sub-second response times, the system implements denormalized data structures to optimize read performance at the cost of some data redundancy.

## Requirements

1. Create a user dashboard that displays user statistics including total posts, comments, likes received, and follower count
2. Show recent user activities with timestamps, activity types, and related content information
3. Implement denormalized storage to avoid expensive JOIN operations during dashboard rendering
4. Ensure dashboard data loads within 200ms for optimal user experience
5. Maintain data consistency between normalized source tables and denormalized dashboard data
6. Support real-time or near real-time updates to dashboard statistics when user activities occur
7. Handle high concurrent read loads without performance degradation
8. Provide fallback mechanisms if denormalized data becomes temporarily inconsistent

## Constraints

1. Dashboard statistics must be eventually consistent with source data within 5 minutes
2. System must handle at least 1000 concurrent dashboard page loads
3. Denormalized data storage overhead should not exceed 20% of total database size
4. All dashboard queries must complete within the 200ms performance requirement
5. Data synchronization processes must not impact primary application performance
6. Dashboard must gracefully handle missing or stale denormalized data

## References

See context.md for existing user model implementations, activity tracking patterns, and current database schema that this dashboard feature builds upon.