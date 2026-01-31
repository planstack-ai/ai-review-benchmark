# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_create_orders_table.php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->string('order_number')->unique();
    $table->enum('status', ['pending', 'processing', 'shipped', 'delivered', 'cancelled', 'failed']);
    $table->decimal('total_amount', 10, 2);
    $table->json('shipping_address');
    $table->string('shipping_method');
    $table->string('tracking_number')->nullable();
    $table->timestamp('shipped_at')->nullable();
    $table->json('shipping_response')->nullable();
    $table->text('shipping_error')->nullable();
    $table->integer('shipping_attempts')->default(0);
    $table->timestamp('last_shipping_attempt')->nullable();
    $table->timestamps();
});

// database/migrations/2024_01_16_create_shipping_logs_table.php
Schema::create('shipping_logs', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained()->cascadeOnDelete();
    $table->string('provider');
    $table->string('action');
    $table->enum('status', ['success', 'error', 'retry']);
    $table->json('request_data')->nullable();
    $table->json('response_data')->nullable();
    $table->text('error_message')->nullable();
    $table->string('error_code')->nullable();
    $table->timestamps();
});
```

## Models

```php
// app/Models/Order.php
class Order extends Model
{
    protected $fillable = [
        'order_number', 'status', 'total_amount', 'shipping_address',
        'shipping_method', 'tracking_number', 'shipped_at', 'shipping_response',
        'shipping_error', 'shipping_attempts', 'last_shipping_attempt'
    ];

    protected $casts = [
        'shipping_address' => 'array',
        'shipping_response' => 'array',
        'shipped_at' => 'datetime',
        'last_shipping_attempt' => 'datetime',
        'total_amount' => 'decimal:2',
    ];

    public const STATUS_PENDING = 'pending';
    public const STATUS_PROCESSING = 'processing';
    public const STATUS_SHIPPED = 'shipped';
    public const STATUS_DELIVERED = 'delivered';
    public const STATUS_CANCELLED = 'cancelled';
    public const STATUS_FAILED = 'failed';

    public const MAX_SHIPPING_ATTEMPTS = 3;

    public function shippingLogs(): HasMany
    {
        return $this->hasMany(ShippingLog::class);
    }

    public function scopeReadyForShipping(Builder $query): void
    {
        $query->where('status', self::STATUS_PROCESSING)
              ->whereNull('tracking_number');
    }

    public function scopeFailedShipping(Builder $query): void
    {
        $query->where('status', self::STATUS_FAILED)
              ->whereNotNull('shipping_error');
    }

    public function canRetryShipping(): bool
    {
        return $this->shipping_attempts < self::MAX_SHIPPING_ATTEMPTS;
    }

    public function markAsShipped(string $trackingNumber, array $response): void
    {
        $this->update([
            'status' => self::STATUS_SHIPPED,
            'tracking_number' => $trackingNumber,
            'shipped_at' => now(),
            'shipping_response' => $response,
            'shipping_error' => null,
        ]);
    }

    public function markShippingFailed(string $error, ?string $errorCode = null): void
    {
        $this->increment('shipping_attempts');
        $this->update([
            'status' => $this->canRetryShipping() ? self::STATUS_PROCESSING : self::STATUS_FAILED,
            'shipping_error' => $error,
            'last_shipping_attempt' => now(),
        ]);
    }
}

// app/Models/ShippingLog.php
class ShippingLog extends Model
{
    protected $fillable = [
        'order_id', 'provider', 'action', 'status', 'request_data',
        'response_data', 'error_message', 'error_code'
    ];

    protected $casts = [
        'request_data' => 'array',
        'response_data' => 'array',
    ];

    public const STATUS_SUCCESS = 'success';
    public const STATUS_ERROR = 'error';
    public const STATUS_RETRY = 'retry';

    public function order(): BelongsTo
    {
        return $this->belongsTo(Order::class);
    }

    public static function logSuccess(int $orderId, string $provider, string $action, array $request, array $response): self
    {
        return self::create([
            'order_id' => $orderId,
            'provider' => $provider,
            'action' => $action,
            'status' => self::STATUS_SUCCESS,
            'request_data' => $request,
            'response_data' => $response,
        ]);
    }

    public static function logError(int $orderId, string $provider, string $action, array $request, string $error, ?string $errorCode = null): self
    {
        return self::create([
            'order_id' => $orderId,
            'provider' => $provider,
            'action' => $action,
            'status' => self::STATUS_ERROR,
            'request_data' => $request,
            'error_message' => $error,
            'error_code' => $errorCode,
        ]);
    }
}
```