# Existing Codebase

## Schema

```sql
CREATE TABLE campaigns (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    budget DECIMAL(19,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE campaign_metrics (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    campaign_id BIGINT NOT NULL,
    impressions BIGINT DEFAULT 0,
    clicks BIGINT DEFAULT 0,
    conversions BIGINT DEFAULT 0,
    spend DECIMAL(19,2) DEFAULT 0.00,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
);
```

## Entities

```java
@Entity
@Table(name = "campaigns")
public class Campaign {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String name;
    
    private String description;
    
    @Column(name = "start_date", nullable = false)
    private LocalDate startDate;
    
    @Column(name = "end_date", nullable = false)
    private LocalDate endDate;
    
    @Column(nullable = false, precision = 19, scale = 2)
    private BigDecimal budget;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private CampaignStatus status;
    
    @CreationTimestamp
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // constructors, getters, setters
}

public enum CampaignStatus {
    DRAFT, ACTIVE, PAUSED, COMPLETED, EXPIRED
}

@Entity
@Table(name = "campaign_metrics")
public class CampaignMetrics {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "campaign_id", nullable = false)
    private Long campaignId;
    
    private Long impressions = 0L;
    private Long clicks = 0L;
    private Long conversions = 0L;
    
    @Column(precision = 19, scale = 2)
    private BigDecimal spend = BigDecimal.ZERO;
    
    @CreationTimestamp
    @Column(name = "recorded_at")
    private LocalDateTime recordedAt;
    
    // constructors, getters, setters
}

@Repository
public interface CampaignRepository extends JpaRepository<Campaign, Long> {
    
    List<Campaign> findByStatus(CampaignStatus status);
    
    @Query("SELECT c FROM Campaign c WHERE c.startDate <= :date AND c.endDate >= :date")
    List<Campaign> findActiveCampaignsOnDate(@Param("date") LocalDate date);
    
    List<Campaign> findByEndDateBefore(LocalDate date);
    
    @Query("SELECT c FROM Campaign c WHERE c.endDate = :date AND c.status = :status")
    List<Campaign> findByEndDateAndStatus(@Param("date") LocalDate date, @Param("status") CampaignStatus status);
}

@Service
public interface CampaignService {
    Campaign createCampaign(Campaign campaign);
    Optional<Campaign> findById(Long id);
    List<Campaign> findActiveCampaigns();
    void updateCampaignStatus(Long campaignId, CampaignStatus status);
    boolean isCampaignActive(Long campaignId);
}

@Component
public class TimeUtils {
    
    public LocalDate getCurrentDate() {
        return LocalDate.now();
    }
    
    public LocalDateTime getCurrentDateTime() {
        return LocalDateTime.now();
    }
    
    public LocalDateTime getEndOfDay(LocalDate date) {
        return date.atTime(LocalTime.MAX);
    }
    
    public LocalDateTime getStartOfDay(LocalDate date) {
        return date.atStartOfDay();
    }
}
```