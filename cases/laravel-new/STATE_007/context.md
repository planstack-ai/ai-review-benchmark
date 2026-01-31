# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_deliveries_table.php
Schema::create('deliveries', function (Blueprint $table) {
    $table->id();
    $table->string('tracking_number')->unique();
    $table->foreignId('order_id')->constrained();
    $table->string('status')->default('pending');
    $table->json('status_history')->nullable();
    $table->timestamp('shipped_at')->nullable();
    $table->timestamp('delivered_at')->nullable();
    $table->timestamps();
    
    $table->index(['status', 'created_at']);
});

// database/migrations/2024_01_15_000002_create_delivery_status_transitions_table.php
Schema::create('delivery_status_transitions', function (Blueprint $table) {
    $table->id();
    $table->string('from_status');
    $table->string('to_status');
    $table->boolean('is_allowed')->default(true);
    $table->timestamps();
    
    $table->unique(['from_status', 'to_status']);
});
```

## Models

```php
// app/Models/Delivery.php
class Delivery extends Model
{
    protected $fillable = [
        'tracking_number',
        'order_id',
        'status',
        'status_history',
        'shipped_at',
        'delivered_at',
    ];

    protected $casts = [
        'status_history' => 'array',
        'shipped_at' => 'datetime',
        'delivered_at' => 'datetime',
    ];

    public const STATUS_PENDING = 'pending';
    public const STATUS_PROCESSING = 'processing';
    public const STATUS_SHIPPED = 'shipped';
    public const STATUS_OUT_FOR_DELIVERY = 'out_for_delivery';
    public const STATUS_DELIVERED = 'delivered';
    public const STATUS_FAILED = 'failed';
    public const STATUS_RETURNED = 'returned';

    public static function getStatusOrder(): array
    {
        return [
            self::STATUS_PENDING => 0,
            self::STATUS_PROCESSING => 1,
            self::STATUS_SHIPPED => 2,
            self::STATUS_OUT_FOR_DELIVERY => 3,
            self::STATUS_DELIVERED => 4,
            self::STATUS_FAILED => 3,
            self::STATUS_RETURNED => 3,
        ];
    }

    public function order(): BelongsTo
    {
        return $this->belongsTo(Order::class);
    }

    public function scopeByStatus(Builder $query, string $status): Builder
    {
        return $query->where('status', $status);
    }

    public function scopeInProgress(Builder $query): Builder
    {
        return $query->whereNotIn('status', [
            self::STATUS_DELIVERED,
            self::STATUS_FAILED,
            self::STATUS_RETURNED,
        ]);
    }

    public function getStatusOrderAttribute(): int
    {
        return self::getStatusOrder()[$this->status] ?? 0;
    }

    public function isDelivered(): bool
    {
        return $this->status === self::STATUS_DELIVERED;
    }

    public function isFinalStatus(): bool
    {
        return in_array($this->status, [
            self::STATUS_DELIVERED,
            self::STATUS_FAILED,
            self::STATUS_RETURNED,
        ]);
    }

    protected function addToStatusHistory(string $fromStatus, string $toStatus): void
    {
        $history = $this->status_history ?? [];
        $history[] = [
            'from' => $fromStatus,
            'to' => $toStatus,
            'timestamp' => now()->toISOString(),
        ];
        $this->status_history = $history;
    }
}

// app/Models/DeliveryStatusTransition.php
class DeliveryStatusTransition extends Model
{
    protected $fillable = [
        'from_status',
        'to_status',
        'is_allowed',
    ];

    protected $casts = [
        'is_allowed' => 'boolean',
    ];

    public static function isTransitionAllowed(string $fromStatus, string $toStatus): bool
    {
        return self::where('from_status', $fromStatus)
            ->where('to_status', $toStatus)
            ->where('is_allowed', true)
            ->exists();
    }
}
```