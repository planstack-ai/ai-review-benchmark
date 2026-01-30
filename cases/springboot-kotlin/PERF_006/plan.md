# User Profile Caching

## Overview

The user profile service needs caching to reduce database load. User profiles are frequently accessed and rarely change.

## Requirements

1. Cache user profile data to reduce database queries
2. Support cache invalidation on profile update
3. Different users must see their own profile data

## Constraints

1. Each user must only see their own data
2. Cache must be thread-safe
