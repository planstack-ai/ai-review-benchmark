# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_orders_table.php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->string('order_number')->unique();
    $table->foreignId('user_id')->constrained();
    $table->decimal('total_amount', 10, 2);
    $table->enum('status', ['pending', 'processing', 'completed', 'cancelled', 'failed']);
    $table->json('metadata')->nullable();
    $table->timestamps();
});

// database/migrations/2024_01_15_000002_create_payments_table.php
Schema::create('payments', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained();
    $table->string('payment_method');
    $table->decimal('amount', 10, 2);
    $table->enum('status', ['pending', 'processing', 'completed', 'failed', 'refunded']);
    $table->string('transaction_id')->nullable();
    $table->json('gateway_response')->nullable();
    $table->timestamp('processed_at')->nullable();
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
        'total_amount',
        'status',
        'metadata',
    ];

    protected $casts = [
        'total_amount' => 'decimal:2',
        'metadata' => 'array',
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function payments(): HasMany
    {
        return $this->hasMany(Payment::class);
    }

    public function scopePending(Builder $query): void
    {
        $query->where('status', 'pending');
    }

    public function markAsProcessing(): bool
    {
        return $this->update(['status' => 'processing']);
    }

    public function markAsCompleted(): bool
    {
        return $this->update(['status' => 'completed']);
    }

    public function markAsFailed(): bool
    {
        return $this->update(['status' => 'failed']);
    }
}

// app/Models/Payment.php
class Payment extends Model
{
    protected $fillable = [
        'order_id',
        'payment_method',
        'amount',
        'status',
        'transaction_id',
        'gateway_response',
        'processed_at',
    ];

    protected $casts = [
        'amount' => 'decimal:2',
        'gateway_response' => 'array',
        'processed_at' => 'datetime',
    ];

    public function order(): BelongsTo
    {
        return $this->belongsTo(Order::class);
    }

    public function scopeCompleted(Builder $query): void
    {
        $query->where('status', 'completed');
    }

    public function markAsCompleted(string $transactionId, array $gatewayResponse = []): bool
    {
        return $this->update([
            'status' => 'completed',
            'transaction_id' => $transactionId,
            'gateway_response' => $gatewayResponse,
            'processed_at' => now(),
        ]);
    }

    public function markAsFailed(array $gatewayResponse = []): bool
    {
        return $this->update([
            'status' => 'failed',
            'gateway_response' => $gatewayResponse,
        ]);
    }
}
```