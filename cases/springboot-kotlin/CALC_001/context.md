# Existing Codebase

## Schema

```sql
CREATE TABLE customers (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    membership_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
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

    @Column(unique = true, nullable = false)
    val email: String,

    @Column(nullable = false)
    val name: String,

    @Enumerated(EnumType.STRING)
    @Column(name = "membership_type", nullable = false)
    val membershipType: MembershipType,

    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime? = null
)

@Entity
@Table(name = "orders")
data class Order(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id", nullable = false)
    val customer: Customer,

    @Column(nullable = false, precision = 10, scale = 2)
    val subtotal: BigDecimal,

    @Column(name = "discount_amount", precision = 10, scale = 2)
    var discountAmount: BigDecimal = BigDecimal.ZERO,

    @Column(name = "total_amount", nullable = false, precision = 10, scale = 2)
    var totalAmount: BigDecimal,

    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime? = null
)

enum class MembershipType {
    GUEST,
    MEMBER,
    PREMIUM
}
```

```kotlin
@Repository
interface CustomerRepository : JpaRepository<Customer, Long> {
    fun findByEmail(email: String): Customer?
    fun findByMembershipType(membershipType: MembershipType): List<Customer>
}

@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByCustomerId(customerId: Long): List<Order>
    fun findByCustomerMembershipType(membershipType: MembershipType): List<Order>
}
```

```kotlin
interface CustomerService {
    fun findByEmail(email: String): Customer?
    fun isMember(customer: Customer): Boolean
}

interface OrderService {
    fun createOrder(customerId: Long, subtotal: BigDecimal): Order
    fun calculateDiscount(customer: Customer, amount: BigDecimal): BigDecimal
}
```

```kotlin
object DiscountConstants {
    val MEMBER_DISCOUNT_RATE = BigDecimal("0.10")
    val HUNDRED = BigDecimal("100")
}

object MathUtils {
    fun percentage(amount: BigDecimal, rate: BigDecimal): BigDecimal {
        return amount.multiply(rate).setScale(2, RoundingMode.HALF_UP)
    }
}
```
