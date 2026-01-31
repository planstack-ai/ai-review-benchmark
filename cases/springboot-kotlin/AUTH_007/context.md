# Existing Codebase

## Schema

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_coupons (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    discount_type VARCHAR(20) NOT NULL,
    discount_value DECIMAL(10,2) NOT NULL,
    expires_at TIMESTAMP,
    is_used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    coupon_id BIGINT,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    final_amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (coupon_id) REFERENCES user_coupons(id)
);
```

## Entities

```kotlin
@Entity
@Table(name = "user_coupons")
data class UserCoupon(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "user_id", nullable = false)
    val userId: Long,

    @Column(nullable = false, unique = true)
    val code: String,

    @Enumerated(EnumType.STRING)
    @Column(name = "discount_type", nullable = false)
    val discountType: DiscountType,

    @Column(name = "discount_value", nullable = false, precision = 10, scale = 2)
    val discountValue: BigDecimal,

    @Column(name = "expires_at")
    val expiresAt: LocalDateTime?,

    @Column(name = "is_used")
    var isUsed: Boolean = false,

    @Column(name = "used_at")
    var usedAt: LocalDateTime? = null
)

enum class DiscountType {
    PERCENTAGE, FIXED_AMOUNT
}

@Repository
interface UserCouponRepository : JpaRepository<UserCoupon, Long> {
    fun findByCode(code: String): UserCoupon?
    fun findByCodeAndUserId(code: String, userId: Long): UserCoupon?
    fun findByUserIdAndIsUsedFalse(userId: Long): List<UserCoupon>
}

data class UserPrincipal(
    val id: Long,
    val email: String
)

class CouponNotFoundException(message: String) : RuntimeException(message)
class CouponExpiredException(message: String) : RuntimeException(message)
class CouponAlreadyUsedException(message: String) : RuntimeException(message)
```
