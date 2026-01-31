# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_payments_table.php
Schema::create('payments', function (Blueprint $table) {
    $table->id();
    $table->string('external_id')->unique();
    $table->string('provider');
    $table->decimal('amount', 10, 2);
    $table->string('currency', 3);
    $table->string('status');
    $table->json('metadata')->nullable();
    $table->timestamps();
    
    $table->index(['provider', 'external_id']);
    $table->index(['status', 'created_at']);
});

// database/migrations/2024_01_15_000002_create_webhook_events_table.php
Schema::create('webhook_events', function (Blueprint $table) {
    $table->id();
    $table->string('webhook_id')->unique();
    $table->string('provider');
    $table->string('event_type');
    $table->json('payload');
    $table->string('status')->default('pending');
    $table->timestamp('processed_at')->nullable();
    $table->timestamps();
    
    $table->index(['provider', 'webhook_id']);
    $table->index(['status', 'created_at']);
});
```

## Models

```php
// app/Models/Payment.php
class Payment extends Model
{
    protected $fillable = [
        'external_id',
        'provider',
        'amount',
        'currency',
        'status',
        'metadata',
    ];

    protected $casts = [
        'amount' => 'decimal:2',
        'metadata' => 'array',
    ];

    public const STATUS_PENDING = 'pending';
    public const STATUS_COMPLETED = 'completed';
    public const STATUS_FAILED = 'failed';
    public const STATUS_CANCELLED = 'cancelled';

    public const PROVIDER_STRIPE = 'stripe';
    public const PROVIDER_PAYPAL = 'paypal';

    public function scopeByProvider(Builder $query, string $provider): Builder
    {
        return $query->where('provider', $provider);
    }

    public function scopeByExternalId(Builder $query, string $externalId): Builder
    {
        return $query->where('external_id', $externalId);
    }

    public function scopeCompleted(Builder $query): Builder
    {
        return $query->where('status', self::STATUS_COMPLETED);
    }

    public function isCompleted(): bool
    {
        return $this->status === self::STATUS_COMPLETED;
    }

    public function isPending(): bool
    {
        return $this->status === self::STATUS_PENDING;
    }
}

// app/Models/WebhookEvent.php
class WebhookEvent extends Model
{
    protected $fillable = [
        'webhook_id',
        'provider',
        'event_type',
        'payload',
        'status',
        'processed_at',
    ];

    protected $casts = [
        'payload' => 'array',
        'processed_at' => 'datetime',
    ];

    public const STATUS_PENDING = 'pending';
    public const STATUS_PROCESSED = 'processed';
    public const STATUS_FAILED = 'failed';

    public function scopeByProvider(Builder $query, string $provider): Builder
    {
        return $query->where('provider', $provider);
    }

    public function scopeByWebhookId(Builder $query, string $webhookId): Builder
    {
        return $query->where('webhook_id', $webhookId);
    }

    public function scopePending(Builder $query): Builder
    {
        return $query->where('status', self::STATUS_PENDING);
    }

    public function markAsProcessed(): void
    {
        $this->update([
            'status' => self::STATUS_PROCESSED,
            'processed_at' => now(),
        ]);
    }

    public function markAsFailed(): void
    {
        $this->update(['status' => self::STATUS_FAILED]);
    }
}
```