# Existing Codebase

## Problem Scenario

```kotlin
// After adding loyaltyPoints column, existing rows have NULL
val customer = customerRepository.findById(id).get()
val points = customer.loyaltyPoints  // null!
val newPoints = points + earnedPoints  // NullPointerException!
```

## Usage Guidelines

- Always define sensible defaults for new columns
- Use @Column(nullable = false) with @ColumnDefault
- In Kotlin, consider non-nullable types with defaults
