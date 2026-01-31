# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_create_payments_table.php
Schema::create('payments', function (Blueprint $table) {
    $table->id();
    $table->string('external_id')->unique();
    $table->foreignId('user_id')->constrained();
    $table->decimal('amount', 10, 2);
    $table->string('currency', 3)->default('USD');
    $table->string('status')->default('pending');
    $table->string('gateway')->index();
    $table->json('gateway_response')->nullable();
    $table->timestamp('gateway_timeout_at')->nullable();
    $table->timestamp('completed_at')->nullable();
    $table->timestamps();
    
    $table->index(['status', 'created_at']);
    $table->index(['gateway', 'status']);
});

// database/migrations/2024_01_16_create_payment_events_table.php
Schema::create('payment_events', function (Blueprint $table) {
    $table->id();
    $table->foreignId('payment_id')->constrained();
    $table->string('event_type');
    $table->json('event_data')->nullable();
    $table->timestamp('occurred_at');
    $table->timestamps();
});
```

## Models

```php
// app/Models/Payment.php
class Payment extends Model
{
    protected $fillable = [
        'external_id',
        'user_id',
        'amount',
        'currency',
        'status',
        'gateway',
        'gateway_response',
        'gateway_timeout_at',
        'completed_at',
    ];

    protected $casts = [
        'amount' => 'decimal:2',
        'gateway_response' => 'array',
        'gateway_timeout_at' => 'datetime',
        'completed_at' => 'datetime',
    ];

    public const STATUS_PENDING = 'pending';
    public const STATUS_PROCESSING = 'processing';
    public const STATUS_COMPLETED = 'completed';
    public const STATUS_FAILED = 'failed';
    public const STATUS_TIMEOUT = 'timeout';
    public const STATUS_CANCELLED = 'cancelled';

    public const GATEWAY_STRIPE = 'stripe';
    public const GATEWAY_PAYPAL = 'paypal';
    public const GATEWAY_SQUARE = 'square';

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function events(): HasMany
    {
        return $this->hasMany(PaymentEvent::class);
    }

    public function scopePending(Builder $query): void
    {
        $query->where('status', self::STATUS_PENDING);
    }

    public function scopeProcessing(Builder $query): void
    {
        $query->where('status', self::STATUS_PROCESSING);
    }

    public function scopeTimedOut(Builder $query): void
    {
        $query->where('status', self::STATUS_TIMEOUT);
    }

    public function scopeStale(Builder $query, int $minutes = 30): void
    {
        $query->whereIn('status', [self::STATUS_PENDING, self::STATUS_PROCESSING])
              ->where('created_at', '<', now()->subMinutes($minutes));
    }

    public function isCompleted(): bool
    {
        return $this->status === self::STATUS_COMPLETED;
    }

    public function isPending(): bool
    {
        return $this->status === self::STATUS_PENDING;
    }

    public function isProcessing(): bool
    {
        return $this->status === self::STATUS_PROCESSING;
    }

    public function hasTimedOut(): bool
    {
        return $this->status === self::STATUS_TIMEOUT;
    }

    public function markAsTimeout(): void
    {
        $this->update([
            'status' => self::STATUS_TIMEOUT,
            'gateway_timeout_at' => now(),
        ]);
    }
}

// app/Models/PaymentEvent.php
class PaymentEvent extends Model
{
    protected $fillable = [
        'payment_id',
        'event_type',
        'event_data',
        'occurred_at',
    ];

    protected $casts = [
        'event_data' => 'array',
        'occurred_at' => 'datetime',
    ];

    public const TYPE_CREATED = 'created';
    public const TYPE_PROCESSING = 'processing';
    public const TYPE_COMPLETED = 'completed';
    public const TYPE_FAILED = 'failed';
    public const TYPE_TIMEOUT = 'timeout';
    public const TYPE_RETRY_ATTEMPTED = 'retry_attempted';

    public function payment(): BelongsTo
    {
        return $this->belongsTo(Payment::class);
    }
}
```