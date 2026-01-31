# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_cache_entries_table.php
Schema::create('cache_entries', function (Blueprint $table) {
    $table->id();
    $table->string('key')->unique();
    $table->text('value');
    $table->integer('expiration');
    $table->timestamps();
    
    $table->index(['key', 'expiration']);
});

// database/migrations/2024_01_15_000002_create_cache_warming_jobs_table.php
Schema::create('cache_warming_jobs', function (Blueprint $table) {
    $table->id();
    $table->string('cache_key');
    $table->string('status')->default('pending');
    $table->json('metadata')->nullable();
    $table->timestamp('started_at')->nullable();
    $table->timestamp('completed_at')->nullable();
    $table->timestamps();
    
    $table->index(['status', 'created_at']);
});
```

## Models

```php
// app/Models/CacheEntry.php
class CacheEntry extends Model
{
    protected $fillable = ['key', 'value', 'expiration'];
    
    protected $casts = [
        'expiration' => 'integer',
    ];
    
    public function scopeExpired(Builder $query): Builder
    {
        return $query->where('expiration', '<', now()->timestamp);
    }
    
    public function scopeActive(Builder $query): Builder
    {
        return $query->where('expiration', '>=', now()->timestamp);
    }
    
    public function scopeByPattern(Builder $query, string $pattern): Builder
    {
        return $query->where('key', 'like', str_replace('*', '%', $pattern));
    }
    
    public function isExpired(): bool
    {
        return $this->expiration < now()->timestamp;
    }
}

// app/Models/CacheWarmingJob.php
class CacheWarmingJob extends Model
{
    const STATUS_PENDING = 'pending';
    const STATUS_RUNNING = 'running';
    const STATUS_COMPLETED = 'completed';
    const STATUS_FAILED = 'failed';
    
    protected $fillable = ['cache_key', 'status', 'metadata', 'started_at', 'completed_at'];
    
    protected $casts = [
        'metadata' => 'array',
        'started_at' => 'datetime',
        'completed_at' => 'datetime',
    ];
    
    public function scopePending(Builder $query): Builder
    {
        return $query->where('status', self::STATUS_PENDING);
    }
    
    public function scopeRunning(Builder $query): Builder
    {
        return $query->where('status', self::STATUS_RUNNING);
    }
    
    public function scopeCompleted(Builder $query): Builder
    {
        return $query->where('status', self::STATUS_COMPLETED);
    }
    
    public function markAsStarted(): void
    {
        $this->update([
            'status' => self::STATUS_RUNNING,
            'started_at' => now(),
        ]);
    }
    
    public function markAsCompleted(): void
    {
        $this->update([
            'status' => self::STATUS_COMPLETED,
            'completed_at' => now(),
        ]);
    }
    
    public function markAsFailed(): void
    {
        $this->update(['status' => self::STATUS_FAILED]);
    }
}

// app/Services/CacheKeyGenerator.php
class CacheKeyGenerator
{
    public static function userProfile(int $userId): string
    {
        return "user.profile.{$userId}";
    }
    
    public static function productCatalog(string $category = 'all'): string
    {
        return "products.catalog.{$category}";
    }
    
    public static function systemSettings(): string
    {
        return 'system.settings';
    }
    
    public static function getCriticalKeys(): array
    {
        return [
            self::systemSettings(),
            self::productCatalog(),
            'navigation.menu',
            'featured.products',
        ];
    }
}
```