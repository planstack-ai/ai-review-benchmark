# Existing Codebase

## Schema

```sql
CREATE TABLE coupons (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE,
    discount_type VARCHAR(20) NOT NULL,
    discount_value DECIMAL(10,2) NOT NULL,
    minimum_order_amount DECIMAL(10,2) DEFAULT 0,
    expires_at TIMESTAMP,
    is_single_use BOOLEAN DEFAULT FALSE,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    coupon_id BIGINT,
    coupon_discount DECIMAL(10,2) DEFAULT 0,
    final_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (coupon_id) REFERENCES coupons(id)
);
```

## Entities

```kotlin
@Entity
@Table(name = "coupons")
data class Coupon(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(nullable = false, unique = true)
    val code: String,

    @Enumerated(EnumType.STRING)
    @Column(name = "discount_type", nullable = false)
    val discountType: DiscountType,

    @Column(name = "discount_value", nullable = false, precision = 10, scale = 2)
    val discountValue: BigDecimal,

    @Column(name = "minimum_order_amount", precision = 10, scale = 2)
    val minimumOrderAmount: BigDecimal = BigDecimal.ZERO,

    @Column(name = "expires_at")
    val expiresAt: LocalDateTime?,

    @Column(name = "is_single_use")
    val isSingleUse: Boolean = false,

    @Column(name = "is_used")
    var isUsed: Boolean = false
)

enum class DiscountType {
    PERCENTAGE, FIXED_AMOUNT
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

    @Column(name = "coupon_id")
    var couponId: Long? = null,

    @Column(name = "coupon_discount", precision = 10, scale = 2)
    var couponDiscount: BigDecimal = BigDecimal.ZERO,

    @Column(name = "final_amount", nullable = false, precision = 10, scale = 2)
    var finalAmount: BigDecimal,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var status: OrderStatus
)

enum class OrderStatus {
    PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
}

@Repository
interface CouponRepository : JpaRepository<Coupon, Long> {
    fun findByCode(code: String): Coupon?
}

@Repository
interface OrderRepository : JpaRepository<Order, Long>

class CouponException(message: String) : RuntimeException(message)
class CouponExpiredException(message: String) : CouponException(message)
class CouponAlreadyUsedException(message: String) : CouponException(message)
class MinimumOrderAmountException(message: String) : CouponException(message)
```
