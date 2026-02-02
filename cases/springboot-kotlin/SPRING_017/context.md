# Context: Order Detail System

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
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100)
);

CREATE TABLE payments (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id),
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_date TIMESTAMP NOT NULL
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

    @OneToMany(mappedBy = "order")
    val items: List<OrderItem> = emptyList(),

    @OneToMany(mappedBy = "order")
    val payments: List<Payment> = emptyList(),

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

    @ManyToOne
    @JoinColumn(name = "product_id")
    val product: Product,

    val quantity: Int,
    val price: BigDecimal
)

@Entity
@Table(name = "products")
data class Product(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    val name: String,

    @Column(columnDefinition = "TEXT")
    val description: String?,

    val category: String
)

@Entity
@Table(name = "payments")
data class Payment(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @ManyToOne
    @JoinColumn(name = "order_id")
    val order: Order,

    val amount: BigDecimal,
    val paymentMethod: String,
    val paymentDate: LocalDateTime
)
```

## Data Scenario

Typical order has:
- 3-5 order items
- 2-3 payment records (split payments)

With @EntityGraph fetching multiple collections eagerly, this creates cartesian product:
- 1 order × 4 items × 3 payments = 12 rows returned
- Data duplicated across rows
- Memory and bandwidth waste
