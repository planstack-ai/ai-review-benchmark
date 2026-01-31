# Existing Codebase

## Schema

```sql
CREATE TABLE bulk_orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    order_type VARCHAR(50) NOT NULL DEFAULT 'BULK',
    total_amount DECIMAL(15,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bulk_order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    unit_price INT NOT NULL,
    quantity INT NOT NULL,
    line_total DECIMAL(15,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES bulk_orders(id)
);

CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    unit_price INT NOT NULL,
    stock_quantity INT NOT NULL
);
```

## Entities

```kotlin
@Entity
@Table(name = "bulk_orders")
data class BulkOrder(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "customer_id", nullable = false)
    val customerId: Long,

    @Column(name = "order_type", nullable = false)
    val orderType: String = "BULK",

    @Column(name = "total_amount", nullable = false, precision = 15, scale = 2)
    var totalAmount: BigDecimal = BigDecimal.ZERO,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var status: OrderStatus,

    @OneToMany(mappedBy = "orderId", cascade = [CascadeType.ALL])
    val items: MutableList<BulkOrderItem> = mutableListOf()
)

@Entity
@Table(name = "bulk_order_items")
data class BulkOrderItem(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "order_id", nullable = false)
    val orderId: Long,

    @Column(name = "product_id", nullable = false)
    val productId: Long,

    @Column(name = "product_name", nullable = false)
    val productName: String,

    @Column(name = "unit_price", nullable = false)
    val unitPrice: Int,

    @Column(nullable = false)
    val quantity: Int,

    @Column(name = "line_total", nullable = false, precision = 15, scale = 2)
    var lineTotal: BigDecimal = BigDecimal.ZERO
)

enum class OrderStatus {
    DRAFT, PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED
}

@Repository
interface BulkOrderRepository : JpaRepository<BulkOrder, Long>

@Repository
interface BulkOrderItemRepository : JpaRepository<BulkOrderItem, Long>

@Repository
interface ProductRepository : JpaRepository<Product, Long>

@Entity
@Table(name = "products")
data class Product(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(nullable = false)
    val name: String,

    @Column(name = "unit_price", nullable = false)
    val unitPrice: Int,

    @Column(name = "stock_quantity", nullable = false)
    val stockQuantity: Int
)
```
