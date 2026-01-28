# Existing Codebase

## Schema

```sql
CREATE TABLE campaigns (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE campaign_products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    campaign_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    discount_percentage DECIMAL(5,2),
    discount_amount DECIMAL(10,2),
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
    
    @Column(name = "start_time", nullable = false)
    private LocalDateTime startTime;
    
    @Column(name = "end_time", nullable = false)
    private LocalDateTime endTime;
    
    @Column(nullable = false)
    private String timezone = "UTC";
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private CampaignStatus status = CampaignStatus.DRAFT;
    
    @CreationTimestamp
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public LocalDateTime getStartTime() { return startTime; }
    public void setStartTime(LocalDateTime startTime) { this.startTime = startTime; }
    
    public LocalDateTime getEndTime() { return endTime; }
    public void setEndTime(LocalDateTime endTime) { this.endTime = endTime; }
    
    public String getTimezone() { return timezone; }
    public void setTimezone(String timezone) { this.timezone = timezone; }
    
    public CampaignStatus getStatus() { return status; }
    public void setStatus(CampaignStatus status) { this.status = status; }
    
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}

public enum CampaignStatus {
    DRAFT, ACTIVE, PAUSED, COMPLETED, CANCELLED
}

@Repository
public interface CampaignRepository extends JpaRepository<Campaign, Long> {
    
    @Query("SELECT c FROM Campaign c WHERE c.status = :status")
    List<Campaign> findByStatus(@Param("status") CampaignStatus status);
    
    @Query("SELECT c FROM Campaign c WHERE c.status = 'ACTIVE' AND c.startTime <= :currentTime AND c.endTime >= :currentTime")
    List<Campaign> findActiveCampaignsAtTime(@Param("currentTime") LocalDateTime currentTime);
    
    Optional<Campaign> findByIdAndStatus(Long id, CampaignStatus status);
}

@Service
public interface CampaignService {
    boolean isCampaignActive(Long campaignId);
    List<Campaign> getActiveCampaigns();
    Optional<Campaign> findById(Long id);
}

public final class TimeZones {
    public static final String UTC = "UTC";
    public static final String JAPAN = "Asia/Tokyo";
    public static final String US_EASTERN = "America/New_York";
    public static final String EUROPE_LONDON = "Europe/London";
    
    private TimeZones() {}
}
```