# Existing Codebase

## Problem Scenario

```kotlin
@Transactional
fun processOrder() {
    1. saveOrder()           // DB write
    2. reserveInventory()    // DB write
    3. chargePayment()       // EXTERNAL API CALL - charges customer
    4. doSomething()         // Throws exception!
    5. Transaction rolls back
    // BUT: Customer was already charged!
}
```

## Usage Guidelines

- Never call external APIs inside database transactions
- Use saga pattern for distributed transactions
