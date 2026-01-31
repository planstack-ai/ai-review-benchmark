# Existing Codebase

## Schema

```sql
CREATE TABLE promotional_campaigns (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    campaign_name VARCHAR(255) NOT NULL,
    subject_line VARCHAR(255) NOT NULL,
    email_content TEXT NOT NULL,
    scheduled_at TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE campaign_recipients (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    campaign_id BIGINT NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255),
    sent_at TIMESTAMP NULL,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    FOREIGN KEY (campaign_id) REFERENCES promotional_campaigns(id)
);

CREATE TABLE admin_notifications (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    notification_type VARCHAR(50) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    context_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Entities

```kotlin
@Entity
@Table(name = "promotional_campaigns")
data class PromotionalCampaign(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "campaign_name", nullable = false)
    val campaignName: String,

    @Column(name = "subject_line", nullable = false)
    val subjectLine: String,

    @Column(name = "email_content", nullable = false, columnDefinition = "TEXT")
    val emailContent: String,

    @Column(name = "scheduled_at", nullable = false)
    val scheduledAt: LocalDateTime,

    @Enumerated(EnumType.STRING)
    val status: CampaignStatus,

    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @OneToMany(mappedBy = "campaign", cascade = [CascadeType.ALL])
    val recipients: List<CampaignRecipient> = emptyList()
)

@Entity
@Table(name = "campaign_recipients")
data class CampaignRecipient(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "campaign_id", nullable = false)
    val campaign: PromotionalCampaign,

    @Column(name = "customer_email", nullable = false)
    val customerEmail: String,

    @Column(name = "customer_name")
    val customerName: String? = null,

    @Column(name = "sent_at")
    var sentAt: LocalDateTime? = null,

    @Enumerated(EnumType.STRING)
    var status: RecipientStatus = RecipientStatus.PENDING,

    @Column(name = "error_message", columnDefinition = "TEXT")
    var errorMessage: String? = null
)

@Entity
@Table(name = "admin_notifications")
data class AdminNotification(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Enumerated(EnumType.STRING)
    @Column(name = "notification_type", nullable = false)
    val notificationType: AdminNotificationType,

    @Enumerated(EnumType.STRING)
    val severity: NotificationSeverity,

    @Column(nullable = false, columnDefinition = "TEXT")
    val message: String,

    @Column(name = "context_data", columnDefinition = "JSON")
    val contextData: String? = null,

    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now()
)

enum class CampaignStatus {
    DRAFT, SCHEDULED, IN_PROGRESS, COMPLETED, FAILED
}

enum class RecipientStatus {
    PENDING, SENT, FAILED, BOUNCED
}

enum class AdminNotificationType {
    EMAIL_FAILURE, SYSTEM_ERROR, PAYMENT_ISSUE, SECURITY_ALERT
}

enum class NotificationSeverity {
    INFO, WARNING, ERROR, CRITICAL
}

@Repository
interface PromotionalCampaignRepository : JpaRepository<PromotionalCampaign, Long> {
    fun findByStatus(status: CampaignStatus): List<PromotionalCampaign>
}

@Repository
interface CampaignRecipientRepository : JpaRepository<CampaignRecipient, Long> {
    fun findByCampaignIdAndStatus(campaignId: Long, status: RecipientStatus): List<CampaignRecipient>
}

@Repository
interface AdminNotificationRepository : JpaRepository<AdminNotification, Long>

interface EmailGatewayService {
    fun sendPromotionalEmail(to: String, subject: String, content: String)
}

@Service
class EmailGatewayServiceImpl : EmailGatewayService {
    private val logger = LoggerFactory.getLogger(EmailGatewayServiceImpl::class.java)

    override fun sendPromotionalEmail(to: String, subject: String, content: String) {
        // Simulate external email service that may fail
        if (to.contains("@invalid.com")) {
            throw EmailServiceException("Invalid email domain")
        }
        if (Math.random() < 0.05) {
            throw EmailServiceException("Email service temporarily unavailable")
        }
        logger.info("Promotional email sent to $to")
    }
}

class EmailServiceException(message: String) : RuntimeException(message)
```
