# FP_007: Complex State Machine

## Overview
Implement a complete order fulfillment state machine with multiple valid state transitions. The implementation must handle all possible state combinations with proper validation and enforce business rules for each transition.

## Requirements
1. Define order states: PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED, RETURNED
2. Implement valid state transitions with business rule validation
3. Use Kotlin sealed class or enum for type-safe state representation
4. Validate all transitions with exhaustive when expressions
5. Throw exceptions for invalid state transitions

## Valid State Transitions
- PENDING -> CONFIRMED, CANCELLED
- CONFIRMED -> PROCESSING, CANCELLED
- PROCESSING -> SHIPPED, CANCELLED
- SHIPPED -> DELIVERED, RETURNED
- DELIVERED -> RETURNED
- CANCELLED -> (terminal state)
- RETURNED -> (terminal state)

## Why This Looks Suspicious But Is Correct
- **Complex nested logic** with many state transitions appears error-prone
- However, this is the **correct implementation** of a complete state machine
- All transitions are **explicitly validated** and invalid paths throw exceptions
- Kotlin's **exhaustive when** ensures no states are missed
- The complexity is **necessary** to properly model real-world order fulfillment

## Implementation Notes
- Use enum class for type-safe state representation
- Exhaustive when expressions ensure all states are handled
- Clear validation for each transition path
- Proper exception handling for invalid transitions
