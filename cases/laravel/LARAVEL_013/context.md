# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_orders_table.php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->string('order_number')->unique();
    $table->foreignId('user_id')->constrained();
    $table->enum('status', ['pending', 'processing', 'completed', 'failed'])->default('pending');
    $table->decimal('total_amount', 10, 2);
    $table->json('items');
    $table->timestamp('processed_at')->nullable();
    $table->timestamps();
    
    $table->index(['status', 'created_at']);
});

// database/migrations/2024_01_15_000002_create_order_notifications_table.php
Schema::create('order_notifications', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained()->onDelete('cascade');
    $table->string('type');
    $table->json('data');
    $table->timestamp('sent_at')->nullable();
    $table->timestamps();
});
```

## Models

```php
// app/Models/Order.php
class Order extends Model
{
    protected $fillable = [
        'order_number',
        'user_id',
        'status',
        'total_amount',
        'items',
        'processed_at'
    ];

    protected $casts = [
        'items' => 'array',
        'total_amount' => 'decimal:2',
        'processed_at' => 'datetime'
    ];

    public const STATUS_PENDING = 'pending';
    public const STATUS_PROCESSING = 'processing';
    public const STATUS_COMPLETED = 'completed';
    public const STATUS_FAILED = 'failed';

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function notifications(): HasMany
    {
        return $this->hasMany(OrderNotification::class);
    }

    public function scopePending(Builder $query): void
    {
        $query->where('status', self::STATUS_PENDING);
    }

    public function scopeProcessing(Builder $query): void
    {
        $query->where('status', self::STATUS_PROCESSING);
    }

    public function markAsProcessing(): bool
    {
        return $this->update([
            'status' => self::STATUS_PROCESSING,
            'processed_at' => now()
        ]);
    }

    public function markAsCompleted(): bool
    {
        return $this->update(['status' => self::STATUS_COMPLETED]);
    }

    public function markAsFailed(): bool
    {
        return $this->update(['status' => self::STATUS_FAILED]);
    }

    public function getTotalItemsAttribute(): int
    {
        return collect($this->items)->sum('quantity');
    }
}

// app/Models/OrderNotification.php
class OrderNotification extends Model
{
    protected $fillable = [
        'order_id',
        'type',
        'data',
        'sent_at'
    ];

    protected $casts = [
        'data' => 'array',
        'sent_at' => 'datetime'
    ];

    public const TYPE_ORDER_CONFIRMATION = 'order_confirmation';
    public const TYPE_PROCESSING_STARTED = 'processing_started';
    public const TYPE_ORDER_COMPLETED = 'order_completed';
    public const TYPE_ORDER_FAILED = 'order_failed';

    public function order(): BelongsTo
    {
        return $this->belongsTo(Order::class);
    }

    public function markAsSent(): bool
    {
        return $this->update(['sent_at' => now()]);
    }
}
```