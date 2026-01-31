# Existing Codebase

## Schema

```sql
CREATE TABLE marketing_campaigns (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    email_body TEXT NOT NULL,
    scheduled_date TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    total_recipients INT DEFAULT 0,
    sent_count INT DEFAULT 0,
    failed_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL
);

CREATE TABLE campaign_subscribers (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unsubscribed_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE campaign_sends (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    campaign_id BIGINT NOT NULL,
    subscriber_id BIGINT NOT NULL,
    status VARCHAR(50) NOT NULL,
    sent_at TIMESTAMP NULL,
    error_message TEXT,
    FOREIGN KEY (campaign_id) REFERENCES marketing_campaigns(id),
    FOREIGN KEY (subscriber_id) REFERENCES campaign_subscribers(id)
);

CREATE TABLE email_rate_limits (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    provider_name VARCHAR(100) NOT NULL,
    max_emails_per_minute INT NOT NULL,
    max_emails_per_hour INT NOT NULL,
    batch_size INT NOT NULL,
    delay_between_batches_ms INT NOT NULL
);
```

## Entities

```kotlin
@Entity
@Table(name = "marketing_campaigns")
data class MarketingCampaign(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(nullable = false)
    val name: String,

    @Column(nullable = false)
    val subject: String,

    @Column(name = "email_body", nullable = false, columnDefinition = "TEXT")
    val emailBody: String,

    @Column(name = "scheduled_date")
    val scheduledDate: LocalDateTime? = null,

    @Enumerated(EnumType.STRING)
    var status: CampaignStatus,

    @Column(name = "total_recipients")
    var totalRecipients: Int = 0,

    @Column(name = "sent_count")
    var sentCount: Int = 0,

    @Column(name = "failed_count")
    var failedCount: Int = 0,

    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(name = "started_at")
    var startedAt: LocalDateTime? = null,

    @Column(name = "completed_at")
    var completedAt: LocalDateTime? = null
)

@Entity
@Table(name = "campaign_subscribers")
data class CampaignSubscriber(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(nullable = false)
    val email: String,

    @Column(name = "full_name")
    val fullName: String? = null,

    @CreationTimestamp
    @Column(name = "subscribed_at")
    val subscribedAt: LocalDateTime = LocalDateTime.now(),

    @Column(name = "unsubscribed_at")
    val unsubscribedAt: LocalDateTime? = null,

    @Column(name = "is_active")
    val isActive: Boolean = true
)

@Entity
@Table(name = "campaign_sends")
data class CampaignSend(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "campaign_id", nullable = false)
    val campaignId: Long,

    @Column(name = "subscriber_id", nullable = false)
    val subscriberId: Long,

    @Enumerated(EnumType.STRING)
    var status: SendStatus,

    @Column(name = "sent_at")
    var sentAt: LocalDateTime? = null,

    @Column(name = "error_message", columnDefinition = "TEXT")
    var errorMessage: String? = null
)

@Entity
@Table(name = "email_rate_limits")
data class EmailRateLimit(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "provider_name", nullable = false)
    val providerName: String,

    @Column(name = "max_emails_per_minute", nullable = false)
    val maxEmailsPerMinute: Int,

    @Column(name = "max_emails_per_hour", nullable = false)
    val maxEmailsPerHour: Int,

    @Column(name = "batch_size", nullable = false)
    val batchSize: Int,

    @Column(name = "delay_between_batches_ms", nullable = false)
    val delayBetweenBatchesMs: Int
)

enum class CampaignStatus {
    DRAFT, SCHEDULED, RUNNING, COMPLETED, PAUSED, FAILED
}

enum class SendStatus {
    PENDING, SENT, FAILED, RATE_LIMITED, BOUNCED
}

@Repository
interface MarketingCampaignRepository : JpaRepository<MarketingCampaign, Long> {
    fun findByStatus(status: CampaignStatus): List<MarketingCampaign>
}

@Repository
interface CampaignSubscriberRepository : JpaRepository<CampaignSubscriber, Long> {
    fun findByIsActiveTrue(): List<CampaignSubscriber>
}

@Repository
interface CampaignSendRepository : JpaRepository<CampaignSend, Long> {
    fun findByCampaignIdAndStatus(campaignId: Long, status: SendStatus): List<CampaignSend>
}

@Repository
interface EmailRateLimitRepository : JpaRepository<EmailRateLimit, Long> {
    fun findByProviderName(providerName: String): EmailRateLimit?
}

interface BulkEmailService {
    fun sendMarketingEmail(to: String, subject: String, body: String)
}

@Service
class BulkEmailServiceImpl : BulkEmailService {
    private val logger = LoggerFactory.getLogger(BulkEmailServiceImpl::class.java)

    override fun sendMarketingEmail(to: String, subject: String, body: String) {
        logger.debug("Sending marketing email to $to")
        Thread.sleep(10)
    }
}
```
