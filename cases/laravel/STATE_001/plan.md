# Order State Machine

## Overview

Manage order lifecycle through defined states.

## Requirements

1. Orders progress through: pending → paid → processing → shipped → delivered
2. Each transition must be valid
3. Only certain transitions are allowed
4. Record state change history

## Valid Transitions

- pending → paid (after payment)
- pending → cancelled (by user or timeout)
- paid → processing (picked for fulfillment)
- paid → refunded (if cancelled after payment)
- processing → shipped (handed to carrier)
- shipped → delivered (confirmed delivery)
