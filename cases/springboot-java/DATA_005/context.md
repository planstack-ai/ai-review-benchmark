# Existing Codebase

## Problem Scenario

```
1. Customer orders "Widget A" at $10.00
2. Order is saved with product_id reference
3. Later, product price is updated to $15.00
4. Customer views order history - shows $15.00 instead of $10.00!
```

## Current Schema

```sql
CREATE TABLE order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,  -- Only stores reference
    quantity INTEGER NOT NULL,
    -- Note: Should also store price_at_purchase, product_name_at_purchase
    created_at TIMESTAMP NOT NULL
);
```

## Service

```java
@Service
public class OrderService {
    public OrderDto getOrderDetails(Long orderId) {
        Order order = orderRepository.findById(orderId).orElseThrow();
        OrderDto dto = new OrderDto();
        dto.setItems(order.getItems().stream().map(item -> {
            ItemDto itemDto = new ItemDto();
            itemDto.setProductName(item.getProduct().getName());  // Gets CURRENT name
            itemDto.setPrice(item.getProduct().getPrice());       // Gets CURRENT price
            itemDto.setQuantity(item.getQuantity());
            return itemDto;
        }).toList());
        return dto;
    }
}
```

## Usage Guidelines

- Snapshot immutable data at transaction time (prices, names)
- Store price_at_purchase in order_item, not just product_id
- Consider temporal tables for complex audit requirements
- Never rely on current master data for historical records
