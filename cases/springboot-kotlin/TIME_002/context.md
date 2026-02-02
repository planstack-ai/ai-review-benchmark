# Existing Codebase

## Schema

```sql
CREATE TABLE campaigns (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    budget DECIMAL(19,2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'DRAFT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE campaign_metrics (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    campaign_id BIGINT NOT NULL,
    impressions BIGINT DEFAULT 0,
    clicks BIGINT DEFAULT 0,
    spend DECIMAL(19,2) DEFAULT 0.00,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    
    val description: String? = null,
    
    @Column(nullable = false, precision = 19, scale = 2)
    val budget: BigDecimal,
    
    @Column(name = "start_date", nullable = false)
    val startDate: LocalDate,
    
    @Column(name = "end_date", nullable = false)
    val endDate: LocalDate,
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val status: CampaignStatus = CampaignStatus.DRAFT,
    
    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now(),
    
    @UpdateTimestamp
    @Column(name = "updated_at")
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
    
    val impressions: Long = 0,
    val clicks: Long = 0,
    
    @Column(precision = 19, scale = 2)
    val spend: BigDecimal = BigDecimal.ZERO,
    
    @CreationTimestamp
    @Column(name = "recorded_at")
    val recordedAt: LocalDateTime = LocalDateTime.now()
)

@Repository
interface CampaignRepository : JpaRepository<Campaign, Long> {
    fun findByStatus(status: CampaignStatus): List<Campaign>
    fun findByStartDateLessThanEqualAndEndDateGreaterThanEqual(
        startDate: LocalDate, 
        endDate: LocalDate
    ): List<Campaign>
}

@Repository
interface CampaignMetricsRepository : JpaRepository<CampaignMetrics, Long> {
    fun findByCampaignIdAndRecordedAtBetween(
        campaignId: Long,
        startTime: LocalDateTime,
        endTime: LocalDateTime
    ): List<CampaignMetrics>
}

@Service
interface CampaignService {
    fun createCampaign(request: CreateCampaignRequest): Campaign
    fun updateCampaignStatus(campaignId: Long, status: CampaignStatus): Campaign
    fun getActiveCampaigns(): List<Campaign>
    fun getCampaignById(id: Long): Campaign?
}

data class CreateCampaignRequest(
    val name: String,
    val description: String? = null,
    val budget: BigDecimal,
    val startDate: LocalDate,
    val endDate: LocalDate
)
```