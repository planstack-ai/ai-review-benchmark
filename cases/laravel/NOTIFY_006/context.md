# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_create_email_providers_table.php
Schema::create('email_providers', function (Blueprint $table) {
    $table->id();
    $table->string('name')->unique();
    $table->string('driver');
    $table->integer('rate_limit_per_minute')->default(60);
    $table->integer('rate_limit_per_hour')->default(1000);
    $table->integer('rate_limit_per_day')->default(10000);
    $table->boolean('is_active')->default(true);
    $table->json('config')->nullable();
    $table->timestamps();
});

// database/migrations/2024_01_16_create_email_rate_limits_table.php
Schema::create('email_rate_limits', function (Blueprint $table) {
    $table->id();
    $table->foreignId('email_provider_id')->constrained()->cascadeOnDelete();
    $table->string('period'); // 'minute', 'hour', 'day'
    $table->integer('sent_count')->default(0);
    $table->timestamp('window_start');
    $table->timestamps();
    
    $table->unique(['email_provider_id', 'period', 'window_start']);
    $table->index(['email_provider_id', 'period', 'window_start']);
});

// database/migrations/2024_01_17_create_notification_jobs_table.php
Schema::create('notification_jobs', function (Blueprint $table) {
    $table->id();
    $table->string('notification_type');
    $table->json('recipients');
    $table->json('data');
    $table->string('status')->default('pending');
    $table->foreignId('email_provider_id')->nullable()->constrained();
    $table->timestamp('scheduled_at')->nullable();
    $table->timestamp('sent_at')->nullable();
    $table->timestamps();
    
    $table->index(['status', 'scheduled_at']);
    $table->index(['email_provider_id', 'status']);
});
```

## Models

```php
// app/Models/EmailProvider.php
class EmailProvider extends Model
{
    protected $fillable = [
        'name',
        'driver',
        'rate_limit_per_minute',
        'rate_limit_per_hour',
        'rate_limit_per_day',
        'is_active',
        'config',
    ];

    protected $casts = [
        'config' => 'array',
        'is_active' => 'boolean',
    ];

    public function rateLimits(): HasMany
    {
        return $this->hasMany(EmailRateLimit::class);
    }

    public function notificationJobs(): HasMany
    {
        return $this->hasMany(NotificationJob::class);
    }

    public function scopeActive(Builder $query): void
    {
        $query->where('is_active', true);
    }

    public function getRateLimitForPeriod(string $period): int
    {
        return match ($period) {
            'minute' => $this->rate_limit_per_minute,
            'hour' => $this->rate_limit_per_hour,
            'day' => $this->rate_limit_per_day,
            default => 0,
        };
    }
}

// app/Models/EmailRateLimit.php
class EmailRateLimit extends Model
{
    protected $fillable = [
        'email_provider_id',
        'period',
        'sent_count',
        'window_start',
    ];

    protected $casts = [
        'window_start' => 'datetime',
    ];

    public function emailProvider(): BelongsTo
    {
        return $this->belongsTo(EmailProvider::class);
    }

    public function scopeForPeriod(Builder $query, string $period): void
    {
        $query->where('period', $period);
    }

    public function scopeCurrentWindow(Builder $query, string $period): void
    {
        $windowStart = $this->getWindowStart($period);
        $query->where('window_start', $windowStart);
    }

    private function getWindowStart(string $period): Carbon
    {
        return match ($period) {
            'minute' => now()->startOfMinute(),
            'hour' => now()->startOfHour(),
            'day' => now()->startOfDay(),
        };
    }
}

// app/Models/NotificationJob.php
class NotificationJob extends Model
{
    const STATUS_PENDING = 'pending';
    const STATUS_PROCESSING = 'processing';
    const STATUS_SENT = 'sent';
    const STATUS_FAILED = 'failed';
    const STATUS_RATE_LIMITED = 'rate_limited';

    protected $fillable = [
        'notification_type',
        'recipients',
        'data',
        'status',
        'email_provider_id',
        'scheduled_at',
        'sent_at',
    ];

    protected $casts = [
        'recipients' => 'array',
        'data' => 'array',
        'scheduled_at' => 'datetime',
        'sent_at' => 'datetime',
    ];

    public function emailProvider(): BelongsTo
    {
        return $this->belongsTo(EmailProvider::class);
    }

    public function scopePending(Builder $query): void
    {
        $query->where('status', self::STATUS_PENDING);
    }

    public function scopeRateLimited(Builder $query): void
    {
        $query->where('status', self::STATUS_RATE_LIMITED);
    }

    public function scopeReadyToSend(Builder $query): void
    {
        $query->whereIn('status', [self::STATUS_PENDING, self::STATUS_RATE_LIMITED])
              ->where(function ($q) {
                  $q->whereNull('scheduled_at')
                    ->orWhere('scheduled_at', '<=', now());
              });
    }

    public function getRecipientCount(): int
    {
        return count($this->recipients);
    }
}
```