# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    shipping_fee DECIMAL(10,2) DEFAULT 0,
    final_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE order_settings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value VARCHAR(255) NOT NULL
);
```

## Entities

```kotlin
@Entity
@Table(name = "orders")
data class Order(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "customer_id", nullable = false)
    val customerId: Long,

    @Column(nullable = false, precision = 10, scale = 2)
    val subtotal: BigDecimal,

    @Column(name = "discount_amount", precision = 10, scale = 2)
    val discountAmount: BigDecimal = BigDecimal.ZERO,

    @Column(name = "shipping_fee", precision = 10, scale = 2)
    val shippingFee: BigDecimal = BigDecimal.ZERO,

    @Column(name = "final_amount", nullable = false, precision = 10, scale = 2)
    val finalAmount: BigDecimal,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var status: OrderStatus
)

enum class OrderStatus {
    DRAFT, PENDING, CONFIRMED, PAID, SHIPPED, DELIVERED, CANCELLED
}

@Repository
interface OrderRepository : JpaRepository<Order, Long>

@Repository
interface OrderSettingsRepository : JpaRepository<OrderSettings, Long> {
    fun findBySettingKey(key: String): OrderSettings?
}

@Entity
@Table(name = "order_settings")
data class OrderSettings(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "setting_key", nullable = false, unique = true)
    val settingKey: String,

    @Column(name = "setting_value", nullable = false)
    val settingValue: String
)

object OrderConstants {
    val DEFAULT_MINIMUM_ORDER_AMOUNT = BigDecimal("1000")
    const val MINIMUM_ORDER_SETTING_KEY = "minimum_order_amount"
}

class MinimumOrderException(
    val currentAmount: BigDecimal,
    val minimumAmount: BigDecimal
) : RuntimeException("Order amount $currentAmount is below minimum $minimumAmount")
```
