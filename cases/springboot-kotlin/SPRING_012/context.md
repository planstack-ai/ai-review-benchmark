# Context: Order Management System

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

## Existing Entities

```kotlin
@Entity
@Table(name = "orders")
data class Order(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    val customerEmail: String,
    val totalAmount: BigDecimal,
    val status: String,

    @OneToMany(mappedBy = "order", cascade = [CascadeType.ALL])
    val items: MutableList<OrderItem> = mutableListOf(),

    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "order_items")
data class OrderItem(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @ManyToOne
    @JoinColumn(name = "order_id")
    val order: Order,

    val productName: String,
    val quantity: Int,
    val price: BigDecimal
)
```

## Email Service Interface

```kotlin
interface EmailService {
    fun sendOrderConfirmation(orderId: Long, customerEmail: String, totalAmount: BigDecimal)
}
```

## Configuration

Spring `@Async` is enabled via `@EnableAsync` annotation in the application configuration.

```kotlin
@Configuration
@EnableAsync
class AsyncConfig {
    @Bean
    fun taskExecutor(): Executor {
        val executor = ThreadPoolTaskExecutor()
        executor.corePoolSize = 2
        executor.maxPoolSize = 5
        executor.queueCapacity = 100
        executor.initialize()
        return executor
    }
}
```
