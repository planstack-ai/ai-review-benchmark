# Existing Codebase

## Problem Scenario

```
@Transactional
public void processOrder() {
    1. saveOrder()           // DB write
    2. reserveInventory()    // DB write
    3. chargePayment()       // EXTERNAL API CALL - charges customer
    4. doSomething()         // Throws exception!
    5. Transaction rolls back
    // BUT: Customer was already charged!
}
```

## The Issue

```java
@Transactional  // Problem: external API call inside transaction
public Order processOrder(OrderRequest request) {
    // These can be rolled back
    Order order = orderRepository.save(createOrder(request));
    inventoryService.reserve(request.getItems());

    // This CANNOT be rolled back - customer is charged!
    paymentService.charge(request.getPaymentToken(), order.getTotal());

    // If this fails, transaction rolls back but payment already happened
    fulfillmentService.createShipment(order);

    return order;
}
```

## Usage Guidelines

- Never call external APIs inside database transactions
- Use saga pattern or choreography for distributed transactions
- Charge payment AFTER all local operations succeed
- Implement compensation logic for rollback scenarios
- Consider eventual consistency for external services
