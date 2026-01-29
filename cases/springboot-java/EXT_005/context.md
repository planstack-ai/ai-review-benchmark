# Existing Codebase

## Race Condition Scenario

```
Time 0: Local inventory = 5, Warehouse = 3
Time 1: Async sync starts, reads warehouse (3)
Time 2: Customer orders 4 items (checks local: 5 >= 4, OK!)
Time 3: Order confirmed with quantity 4
Time 4: Sync completes, sets local = 3
Time 5: Actual inventory is 3, but 4 were sold!
         Result: Oversold by 1 item
```

## Current Sync Pattern

```java
@Scheduled(fixedRate = 60000)
@Async
public void syncInventory() {
    List<InventoryUpdate> updates = warehouseClient.getInventoryLevels();
    for (InventoryUpdate update : updates) {
        // This overwrites local quantity without considering pending orders
        inventoryRepository.updateQuantity(update.getProductId(), update.getQuantity());
    }
}
```

## Usage Guidelines

- Consider pending/reserved quantities during sync
- Use versioning or timestamps to detect stale updates
- Implement distributed locking for critical sections
- Queue inventory changes instead of direct updates
- Consider event sourcing for audit trail
