# Context: Order API Validation

## Database Schema

```sql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    customer_email VARCHAR(255) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id),
    product_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);
```

## Existing Service

```kotlin
@Service
class OrderService(
    private val orderRepository: OrderRepository
) {
    fun createOrder(request: OrderRequest): Order {
        val totalAmount = request.items.sumOf { it.price * it.quantity.toBigDecimal() }

        val order = Order(
            customerEmail = request.customerEmail,
            totalAmount = totalAmount,
            status = "PENDING"
        )

        request.items.forEach { itemRequest ->
            val orderItem = OrderItem(
                order = order,
                productName = itemRequest.productName,
                quantity = itemRequest.quantity,
                price = itemRequest.price
            )
            order.items.add(orderItem)
        }

        return orderRepository.save(order)
    }
}
```

## Validation Dependencies

Spring Boot Validation starter is included:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

## Expected Validation Rules

- Customer email: required, not blank
- Items list: not empty
- Each item's product name: not blank
- Each item's quantity: positive (> 0)
- Each item's price: positive (> 0)
