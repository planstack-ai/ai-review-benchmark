# Context: Country Code Reference System

## Overview

The system provides country code lookups for address validation, phone number formatting, and internationalization. Country codes are queried on nearly every API request, making cache warming a critical performance optimization.

## Database Schema

```sql
CREATE TABLE countries (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(2) NOT NULL UNIQUE,    -- ISO 3166-1 alpha-2
    code3 VARCHAR(3) NOT NULL UNIQUE,   -- ISO 3166-1 alpha-3
    name VARCHAR(255) NOT NULL,
    numeric_code VARCHAR(3),            -- ISO 3166-1 numeric
    phone_prefix VARCHAR(10),
    currency_code VARCHAR(3),
    region VARCHAR(50),
    subregion VARCHAR(50),
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_countries_code ON countries(code);
CREATE INDEX idx_countries_code3 ON countries(code3);
CREATE INDEX idx_countries_active ON countries(active);

-- Sample data
INSERT INTO countries (code, code3, name, numeric_code, phone_prefix, currency_code, region, subregion) VALUES
('US', 'USA', 'United States', '840', '+1', 'USD', 'Americas', 'Northern America'),
('JP', 'JPN', 'Japan', '392', '+81', 'JPY', 'Asia', 'Eastern Asia'),
('GB', 'GBR', 'United Kingdom', '826', '+44', 'GBP', 'Europe', 'Northern Europe');
-- ... 247 more rows (250 total)
```

## Dataset Characteristics

```
Total rows: 250 (all countries in the world)
Row size: ~200 bytes average
Total size: 250 × 200 = 50KB

Growth rate: 0-1 new countries per decade
Last addition: South Sudan (2011)
Next expected: None in foreseeable future

Update frequency: 1-2 changes per year (name changes, status updates)
Update impact: Cache refresh via @CacheEvict on update
```

## Access Patterns

Analysis of production traffic over 24 hours:

```
Total API requests: 14,400,000 (10,000/minute)
Requests querying country data: 12,960,000 (90%)
Unique country codes queried: 150 (60% of total)

Most queried (top 10):
- US: 4,320,000 queries
- GB: 1,440,000 queries
- JP: 1,080,000 queries
- DE: 720,000 queries
- FR: 576,000 queries
- ... (other countries)

Query types:
- By ISO code (code): 80%
- By ISO3 code (code3): 15%
- By name: 5%

Read-to-write ratio: >1,000,000:1
(Millions of reads per day, ~1 write per year)
```

## Performance Impact Analysis

### Without Cache Warming

```
Query: SELECT * FROM countries WHERE code = ?
Database execution time: 5ms (indexed query)
Network latency: 1ms
Total: 6ms per request

Total database time per minute:
10,000 requests × 6ms = 60,000ms = 1 minute

Database is 100% utilized just serving country lookups.
No capacity for other queries.
```

### With Cache Warming

```
Cache lookup time: 0.01ms (in-memory HashMap)
Database queries: 0 per minute
Database utilization: 0%

Total cache time per minute:
10,000 requests × 0.01ms = 100ms

Performance improvement: 600x faster
Database capacity freed: 100%
```

## Memory Usage Analysis

```
Country entity size breakdown:
- Object header: 16 bytes
- Long id: 8 bytes
- String code (2 chars): ~40 bytes
- String code3 (3 chars): ~42 bytes
- String name (avg 15 chars): ~70 bytes
- Other fields: ~24 bytes
Total per entity: ~200 bytes

Total memory usage:
250 countries × 200 bytes = 50KB

HashMap overhead (load factor 0.75):
250 / 0.75 = 334 slots × 40 bytes = 13KB

Total cache memory: 63KB

Typical JVM heap: 2GB
Cache percentage: 0.003%
Impact: Negligible
```

## Cache Invalidation Strategy

```kotlin
/**
 * Rare updates to country data trigger cache refresh.
 * This happens 1-2 times per year in practice.
 */
@Service
class CountryUpdateService {

    @CacheEvict(value = ["countries"], allEntries = true)
    @Transactional
    fun updateCountry(code: String, updates: CountryUpdate) {
        // Update country data
        // Cache will be automatically refreshed on next access
    }
}
```

## Industry Precedents

This cache warming pattern is used by:

1. **Spring Boot itself**: Loads all registered beans into ApplicationContext
2. **Hibernate**: Loads entity metadata and mappings on startup
3. **AWS SDK**: Caches service endpoints and region data
4. **Google Cloud SDK**: Caches zone and region information
5. **Every major framework**: Caches static configuration data

Reference data caching is a universally accepted optimization.

## Alternative Approaches Considered

### Alternative 1: Query database on demand
**Rejected**:
- 10,000 queries/minute would saturate database
- 6ms latency per request unacceptable
- Indexes help but still require disk I/O

### Alternative 2: Lazy cache population
**Rejected**:
- Cold start penalty on first request
- Inconsistent latency
- Cache miss storms on restart

### Alternative 3: External cache (Redis)
**Rejected**:
- Adds network latency (1-2ms)
- Extra infrastructure complexity
- Still slower than in-memory
- Overkill for 50KB dataset

### Chosen: In-memory cache warming on startup
**Selected**:
- Fastest possible lookups (0.01ms)
- Zero database load
- Predictable performance
- Simple implementation
- Industry standard pattern
