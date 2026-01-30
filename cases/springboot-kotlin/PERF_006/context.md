# Existing Codebase

## Cache Configuration

```kotlin
@Configuration
@EnableCaching
class CacheConfig {
    @Bean
    fun cacheManager(): CacheManager {
        val cacheManager = SimpleCacheManager()
        cacheManager.setCaches(listOf(
            ConcurrentMapCache("userProfile"),
            ConcurrentMapCache("productCatalog")
        ))
        return cacheManager
    }
}
```

## Usage Guidelines

- Always include unique identifiers in cache keys to prevent data leakage
- Use `@Cacheable(value = "cacheName", key = "#uniqueId")` pattern
- Invalidate cache on updates with `@CacheEvict`
