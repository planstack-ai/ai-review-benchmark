# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_orders_table.php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->string('order_number')->unique();
    $table->enum('status', ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']);
    $table->decimal('total_amount', 10, 2);
    $table->foreignId('user_id')->constrained();
    $table->timestamp('confirmed_at')->nullable();
    $table->timestamp('shipped_at')->nullable();
    $table->timestamp('delivered_at')->nullable();
    $table->timestamps();
});

// database/migrations/2024_01_15_000002_create_order_events_table.php
Schema::create('order_events', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained()->cascadeOnDelete();
    $table->string('event_type');
    $table->json('event_data')->nullable();
    $table->integer('sequence_number');
    $table->timestamp('processed_at')->nullable();
    $table->timestamps();
    
    $table->index(['order_id', 'sequence_number']);
    $table->unique(['order_id', 'event_type', 'sequence_number']);
});
```

## Models

```php
// app/Models/Order.php
class Order extends Model
{
    protected $fillable = [
        'order_number',
        'status',
        'total_amount',
        'user_id',
        'confirmed_at',
        'shipped_at',
        'delivered_at',
    ];

    protected $casts = [
        'total_amount' => 'decimal:2',
        'confirmed_at' => 'datetime',
        'shipped_at' => 'datetime',
        'delivered_at' => 'datetime',
    ];

    public const STATUS_PENDING = 'pending';
    public const STATUS_CONFIRMED = 'confirmed';
    public const STATUS_PROCESSING = 'processing';
    public const STATUS_SHIPPED = 'shipped';
    public const STATUS_DELIVERED = 'delivered';
    public const STATUS_CANCELLED = 'cancelled';

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function events(): HasMany
    {
        return $this->hasMany(OrderEvent::class);
    }

    public function scopePendingProcessing(Builder $query): void
    {
        $query->whereIn('status', [self::STATUS_PENDING, self::STATUS_CONFIRMED]);
    }

    public function canTransitionTo(string $status): bool
    {
        $transitions = [
            self::STATUS_PENDING => [self::STATUS_CONFIRMED, self::STATUS_CANCELLED],
            self::STATUS_CONFIRMED => [self::STATUS_PROCESSING, self::STATUS_CANCELLED],
            self::STATUS_PROCESSING => [self::STATUS_SHIPPED, self::STATUS_CANCELLED],
            self::STATUS_SHIPPED => [self::STATUS_DELIVERED],
        ];

        return in_array($status, $transitions[$this->status] ?? []);
    }
}

// app/Models/OrderEvent.php
class OrderEvent extends Model
{
    protected $fillable = [
        'order_id',
        'event_type',
        'event_data',
        'sequence_number',
        'processed_at',
    ];

    protected $casts = [
        'event_data' => 'array',
        'processed_at' => 'datetime',
    ];

    public const EVENT_CREATED = 'order.created';
    public const EVENT_CONFIRMED = 'order.confirmed';
    public const EVENT_PAYMENT_PROCESSED = 'payment.processed';
    public const EVENT_INVENTORY_RESERVED = 'inventory.reserved';
    public const EVENT_SHIPPED = 'order.shipped';
    public const EVENT_DELIVERED = 'order.delivered';
    public const EVENT_CANCELLED = 'order.cancelled';

    public function order(): BelongsTo
    {
        return $this->belongsTo(Order::class);
    }

    public function scopeUnprocessed(Builder $query): void
    {
        $query->whereNull('processed_at');
    }

    public function scopeBySequence(Builder $query): void
    {
        $query->orderBy('sequence_number');
    }

    public function scopeForOrder(Builder $query, int $orderId): void
    {
        $query->where('order_id', $orderId);
    }

    public function markAsProcessed(): void
    {
        $this->update(['processed_at' => now()]);
    }
}
```