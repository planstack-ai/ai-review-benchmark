# Existing Codebase

## Schema

```sql
CREATE TABLE campaigns (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    budget DECIMAL(19,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE TABLE campaign_metrics (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    campaign_id BIGINT NOT NULL,
    impressions BIGINT DEFAULT 0,
    clicks BIGINT DEFAULT 0,
    spend DECIMAL(19,2) DEFAULT 0.00,
    recorded_at DATETIME NOT NULL,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
);
```

## Entities

```kotlin
@Entity
@Table(name = "campaigns")
data class Campaign(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(nullable = false)
    val name: String,
    
    @Column(name = "start_date", nullable = false)
    val startDate: LocalDateTime,
    
    @Column(name = "end_date", nullable = false)
    val endDate: LocalDateTime,
    
    @Column(nullable = false, precision = 19, scale = 2)
    val budget: BigDecimal,
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val status: CampaignStatus,
    
    @Column(name = "created_at", nullable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),
    
    @Column(name = "updated_at", nullable = false)
    val updatedAt: LocalDateTime = LocalDateTime.now()
)

enum class CampaignStatus {
    DRAFT, ACTIVE, PAUSED, COMPLETED, CANCELLED
}

@Entity
@Table(name = "campaign_metrics")
data class CampaignMetrics(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "campaign_id", nullable = false)
    val campaignId: Long,
    
    @Column(nullable = false)
    val impressions: Long = 0,
    
    @Column(nullable = false)
    val clicks: Long = 0,
    
    @Column(nullable = false, precision = 19, scale = 2)
    val spend: BigDecimal = BigDecimal.ZERO,
    
    @Column(name = "recorded_at", nullable = false)
    val recordedAt: LocalDateTime
)

@Repository
interface CampaignRepository : JpaRepository<Campaign, Long> {
    fun findByStatus(status: CampaignStatus): List<Campaign>
    
    @Query("SELECT c FROM Campaign c WHERE c.status = :status AND c.startDate <= :currentTime AND c.endDate >= :currentTime")
    fun findActiveInTimeRange(status: CampaignStatus, currentTime: LocalDateTime): List<Campaign>
}

@Repository
interface CampaignMetricsRepository : JpaRepository<CampaignMetrics, Long> {
    fun findByCampaignIdOrderByRecordedAtDesc(campaignId: Long): List<CampaignMetrics>
}

@Service
interface CampaignService {
    fun getActiveCampaigns(): List<Campaign>
    fun getCampaignMetrics(campaignId: Long): List<CampaignMetrics>
}

object TimeZones {
    val JAPAN: ZoneId = ZoneId.of("Asia/Tokyo")
    val UTC: ZoneId = ZoneId.of("UTC")
}

object CampaignConstants {
    const val DEFAULT_PAGE_SIZE = 20
    const val MAX_CAMPAIGN_DURATION_DAYS = 365L
}
```