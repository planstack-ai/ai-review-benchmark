# Laravel Eloquent Model with Global Scope Implementation

## Overview

This feature implements a Laravel Eloquent model that automatically applies a global scope during the model's boot process. The global scope should filter records based on a specific condition that applies to all queries for this model unless explicitly removed. This is commonly used for soft deletes, tenant filtering, or status-based filtering across an application.

## Requirements

1. Create an Eloquent model class that extends Laravel's base Model class
2. Implement the static `boot()` method to register a global scope
3. The global scope must filter records based on an `active` status field
4. The global scope should only return records where `active` equals `true` or `1`
5. The global scope must be applied automatically to all queries (select, update, delete)
6. Provide a method to bypass the global scope when needed
7. The model should call the parent `boot()` method to maintain Laravel's default boot behavior
8. The global scope should be implemented using Laravel's `addGlobalScope()` method
9. The scope should have a unique identifier name for potential removal
10. The model should include appropriate fillable fields for mass assignment

## Constraints

1. The global scope must not interfere with explicit `withTrashed()` or similar scope methods
2. The active field must be treated as a boolean value in the scope condition
3. The scope should handle both boolean `true/false` and integer `1/0` values for the active field
4. The implementation must be compatible with Laravel's query builder methods
5. The global scope should not be applied when using `withoutGlobalScope()` method
6. The model must maintain all standard Eloquent functionality while the scope is active

## References

See context.md for examples of existing Laravel Eloquent implementations and global scope patterns used in the codebase.