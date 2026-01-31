# Existing Codebase

## Schema

```sql
CREATE TABLE subscriptions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    plan_id BIGINT NOT NULL,
    status VARCHAR(50) NOT NULL,
    billing_date DATE NOT NULL,
    next_billing_date DATE NOT NULL,
    monthly_amount DECIMAL(19,2) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (plan_id) REFERENCES subscription_plans(id)
);

CREATE TABLE subscription_plans (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    monthly_price DECIMAL(19,2) NOT NULL,
    features TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE billing_history (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    subscription_id BIGINT NOT NULL,
    billing_date DATE NOT NULL,
    amount DECIMAL(19,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    processed_at DATETIME,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
);
```

## Entities

```kotlin
@Entity
@Table(name = "subscriptions")
data class Subscription(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "customer_id", nullable = false)
    val customerId: Long,

    @Column(name = "plan_id", nullable = false)
    val planId: Long,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val status: SubscriptionStatus,

    @Column(name = "billing_date", nullable = false)
    val billingDate: LocalDate,

    @Column(name = "next_billing_date", nullable = false)
    val nextBillingDate: LocalDate,

    @Column(name = "monthly_amount", nullable = false, precision = 19, scale = 2)
    val monthlyAmount: BigDecimal,

    @Column(name = "created_at", nullable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(name = "updated_at", nullable = false)
    val updatedAt: LocalDateTime = LocalDateTime.now()
)

enum class SubscriptionStatus {
    ACTIVE, PAUSED, CANCELLED, EXPIRED
}

@Entity
@Table(name = "subscription_plans")
data class SubscriptionPlan(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(nullable = false)
    val name: String,

    @Column(columnDefinition = "TEXT")
    val description: String?,

    @Column(name = "monthly_price", nullable = false, precision = 19, scale = 2)
    val monthlyPrice: BigDecimal,

    @Column(columnDefinition = "TEXT")
    val features: String?,

    @Column(nullable = false)
    val active: Boolean = true
)

@Entity
@Table(name = "billing_history")
data class BillingHistory(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "subscription_id", nullable = false)
    val subscriptionId: Long,

    @Column(name = "billing_date", nullable = false)
    val billingDate: LocalDate,

    @Column(nullable = false, precision = 19, scale = 2)
    val amount: BigDecimal,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val status: BillingStatus,

    @Column(name = "processed_at")
    val processedAt: LocalDateTime?
)

enum class BillingStatus {
    PENDING, PROCESSED, FAILED, REFUNDED
}

@Repository
interface SubscriptionRepository : JpaRepository<Subscription, Long> {
    fun findByCustomerId(customerId: Long): List<Subscription>
    fun findByStatus(status: SubscriptionStatus): List<Subscription>
    fun findByNextBillingDateLessThanEqual(date: LocalDate): List<Subscription>
}

@Repository
interface SubscriptionPlanRepository : JpaRepository<SubscriptionPlan, Long> {
    fun findByActiveTrue(): List<SubscriptionPlan>
}

@Repository
interface BillingHistoryRepository : JpaRepository<BillingHistory, Long> {
    fun findBySubscriptionIdOrderByBillingDateDesc(subscriptionId: Long): List<BillingHistory>
}

@Service
interface BillingService {
    fun processDueBillings(currentDate: LocalDate): BillingResult
    fun calculateNextBillingDate(currentBillingDate: LocalDate): LocalDate
    fun createSubscription(customerId: Long, planId: Long, startDate: LocalDate): Subscription
}

object SubscriptionConstants {
    const val GRACE_PERIOD_DAYS = 3
    const val MAX_RETRY_ATTEMPTS = 3
    val TRIAL_PERIOD_DAYS = 14
}

data class BillingResult(
    val processed: Int,
    val failed: Int,
    val totalAmount: BigDecimal
)
```
