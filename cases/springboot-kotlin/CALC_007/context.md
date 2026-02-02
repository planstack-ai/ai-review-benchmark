# Existing Codebase

## Schema

```sql
CREATE TABLE customers (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    membership_type VARCHAR(50) NOT NULL,
    total_points BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    final_amount DECIMAL(10,2) NOT NULL,
    points_earned INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE point_transactions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    order_id BIGINT,
    points INT NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

## Entities

```kotlin
@Entity
@Table(name = "customers")
data class Customer(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(nullable = false, unique = true)
    val email: String,

    @Enumerated(EnumType.STRING)
    @Column(name = "membership_type", nullable = false)
    val membershipType: MembershipType,

    @Column(name = "total_points")
    var totalPoints: Long = 0,

    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now()
)

enum class MembershipType {
    GUEST, MEMBER, PREMIUM
}

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

    @Column(name = "final_amount", nullable = false, precision = 10, scale = 2)
    val finalAmount: BigDecimal,

    @Column(name = "points_earned")
    var pointsEarned: Int = 0,

    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "point_transactions")
data class PointTransaction(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "customer_id", nullable = false)
    val customerId: Long,

    @Column(name = "order_id")
    val orderId: Long?,

    @Column(nullable = false)
    val points: Int,

    @Enumerated(EnumType.STRING)
    @Column(name = "transaction_type", nullable = false)
    val transactionType: PointTransactionType,

    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now()
)

enum class PointTransactionType {
    EARNED, REDEEMED, EXPIRED, ADJUSTED
}

@Repository
interface CustomerRepository : JpaRepository<Customer, Long> {
    fun findByEmail(email: String): Customer?
}

@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByCustomerId(customerId: Long): List<Order>
}

@Repository
interface PointTransactionRepository : JpaRepository<PointTransaction, Long> {
    fun findByCustomerId(customerId: Long): List<PointTransaction>
}

object PointsConstants {
    const val POINTS_PER_YEN = 100
    const val MAX_POINTS_PER_TRANSACTION = 10000
}
```
