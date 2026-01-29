# Existing Codebase

## Concurrent Update Scenario

```
Thread A: reads inventory (quantity = 100)
Thread B: reads inventory (quantity = 100)
Thread A: decrements by 5, saves (quantity = 95)
Thread B: decrements by 3, saves (quantity = 97)  -- Thread A's update is lost!
```

## Service

```java
@Service
public class InventoryService {
    @Autowired
    private InventoryRepository inventoryRepository;

    @Transactional
    public void decrementStock(Long productId, int quantity) {
        Inventory inventory = inventoryRepository.findByProductId(productId)
            .orElseThrow(() -> new IllegalArgumentException("Product not found"));

        int newQuantity = inventory.getQuantity() - quantity;
        if (newQuantity < 0) {
            throw new InsufficientStockException("Not enough stock");
        }

        inventory.setQuantity(newQuantity);
        inventoryRepository.save(inventory);
    }
}
```

## Usage Guidelines

- Use @Version for optimistic locking on entities with concurrent updates
- Handle OptimisticLockException with retry logic
- Consider pessimistic locking for high-contention scenarios
- Test concurrent access patterns thoroughly
