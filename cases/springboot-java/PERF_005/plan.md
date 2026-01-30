# Customer Search Service

## Overview

The customer service team needs to search for customers by various criteria including email, phone number, and name. The search must be fast to ensure good customer service response times.

## Requirements

1. Search customers by email address
2. Search customers by phone number
3. Search customers by name (partial match)
4. Search results must return quickly for service representatives
5. Support searching across millions of customer records

## Constraints

1. Search response time must be under 200ms
2. Phone number format varies (with/without country code)
3. Email search must be exact match
4. Name search should support partial matching

## References

See context.md for existing schema and indexes.
