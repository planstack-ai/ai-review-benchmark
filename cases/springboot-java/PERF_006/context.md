# Existing Codebase

## Cache Configuration

```java
@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    public CacheManager cacheManager() {
        SimpleCacheManager cacheManager = new SimpleCacheManager();
        cacheManager.setCaches(Arrays.asList(
            new ConcurrentMapCache("userProfile"),
            new ConcurrentMapCache("productCatalog"),
            new ConcurrentMapCache("orderHistory")
        ));
        return cacheManager;
    }
}
```

## Entity

```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String email;
    private String firstName;
    private String lastName;
    private String phone;
    private String address;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    // getters and setters
}
```

## Usage Guidelines

- Always include unique identifiers in cache keys to prevent data leakage
- Use `@Cacheable(value = "cacheName", key = "#uniqueId")` pattern
- Invalidate cache on updates with `@CacheEvict`
- Consider cache key design for multi-tenant applications
