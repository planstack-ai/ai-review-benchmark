<?php

namespace App\Services;

use App\Models\CacheEntry;
use App\Models\CacheWarmingJob;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Collection;

class CacheWarmingService
{
    public function __construct(
        private readonly CacheKeyGenerator $keyGenerator
    ) {}

    public function warmCriticalCaches(): void
    {
        $criticalKeys = CacheKeyGenerator::getCriticalKeys();
        
        foreach ($criticalKeys as $key) {
            $this->scheduleWarmingJob($key, ['priority' => 'high']);
        }
    }

    public function warmUserCaches(array $userIds): void
    {
        foreach ($userIds as $userId) {
            $key = CacheKeyGenerator::userProfile($userId);
            $this->scheduleWarmingJob($key, ['user_id' => $userId]);
        }
    }

    public function warmProductCaches(array $categories = ['all']): void
    {
        foreach ($categories as $category) {
            $key = CacheKeyGenerator::productCatalog($category);
            $this->scheduleWarmingJob($key, ['category' => $category]);
        }
    }

    public function processWarmingJobs(int $batchSize = 10): int
    {
        $jobs = CacheWarmingJob::pending()
            ->orderBy('created_at')
            ->limit($batchSize)
            ->get();

        $processed = 0;
        
        foreach ($jobs as $job) {
            if ($this->processWarmingJob($job)) {
                $processed++;
            }
        }

        return $processed;
    }

    public function cleanupExpiredEntries(): int
    {
        return CacheEntry::expired()->delete();
    }

    public function getWarmingStatus(): array
    {
        return [
            'pending' => CacheWarmingJob::pending()->count(),
            'running' => CacheWarmingJob::running()->count(),
            'completed' => CacheWarmingJob::completed()->count(),
            'failed' => CacheWarmingJob::where('status', CacheWarmingJob::STATUS_FAILED)->count(),
        ];
    }

    private function scheduleWarmingJob(string $cacheKey, array $metadata = []): CacheWarmingJob
    {
        return CacheWarmingJob::create([
            'cache_key' => $cacheKey,
            'metadata' => $metadata,
        ]);
    }

    private function processWarmingJob(CacheWarmingJob $job): bool
    {
        try {
            $job->markAsStarted();
            
            $value = $this->generateCacheValue($job->cache_key, $job->metadata);
            
            if ($value !== null) {
                $this->storeCacheEntry($job->cache_key, $value);
                $job->markAsCompleted();
                return true;
            }
            
            $job->markAsFailed();
            return false;
        } catch (\Exception $e) {
            Log::error('Cache warming job failed', [
                'job_id' => $job->id,
                'cache_key' => $job->cache_key,
                'error' => $e->getMessage(),
            ]);
            
            $job->markAsFailed();
            return false;
        }
    }

    private function generateCacheValue(string $key, array $metadata): mixed
    {
        if (str_starts_with($key, 'user.profile.')) {
            return $this->generateUserProfileData($metadata['user_id'] ?? null);
        }
        
        if (str_starts_with($key, 'products.catalog.')) {
            return $this->generateProductCatalogData($metadata['category'] ?? 'all');
        }
        
        return $this->generateGenericCacheData($key);
    }

    private function generateUserProfileData(?int $userId): ?array
    {
        if (!$userId) return null;
        
        return [
            'id' => $userId,
            'preferences' => ['theme' => 'dark', 'language' => 'en'],
            'cached_at' => now()->toISOString(),
        ];
    }

    private function generateProductCatalogData(string $category): array
    {
        return [
            'category' => $category,
            'products' => [],
            'total_count' => 0,
            'cached_at' => now()->toISOString(),
        ];
    }

    private function generateGenericCacheData(string $key): array
    {
        return [
            'key' => $key,
            'data' => [],
            'cached_at' => now()->toISOString(),
        ];
    }

    private function storeCacheEntry(string $key, mixed $value): void
    {
        $expiration = now()->addHours(24)->timestamp;
        
        CacheEntry::updateOrCreate(
            ['key' => $key],
            [
                'value' => json_encode($value),
                'expiration' => $expiration,
            ]
        );
        
        Cache::put($key, $value, $expiration);
    }
}