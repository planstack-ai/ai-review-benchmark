# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_payments_table.php
Schema::create('payments', function (Blueprint $table) {
    $table->id();
    $table->string('transaction_id')->unique();
    $table->string('gateway')->index();
    $table->decimal('amount', 10, 2);
    $table->string('currency', 3);
    $table->enum('status', ['pending', 'processing', 'completed', 'failed', 'refunded']);
    $table->json('gateway_response')->nullable();
    $table->morphs('payable');
    $table->timestamps();
});

// database/migrations/2024_01_15_000002_create_orders_table.php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->string('order_number')->unique();
    $table->foreignId('user_id')->constrained();
    $table->decimal('total', 10, 2);
    $table->string('currency', 3)->default('USD');
    $table->enum('status', ['pending', 'paid', 'shipped', 'delivered', 'cancelled']);
    $table->timestamps();
});
```

## Models

```php
// app/Models/Payment.php
class Payment extends Model
{
    protected $fillable = [
        'transaction_id',
        'gateway',
        'amount',
        'currency',
        'status',
        'gateway_response',
        'payable_type',
        'payable_id',
    ];

    protected $casts = [
        'amount' => 'decimal:2',
        'gateway_response' => 'array',
    ];

    public function payable(): MorphTo
    {
        return $this->morphTo();
    }

    public function scopeSuccessful(Builder $query): void
    {
        $query->where('status', 'completed');
    }

    public function scopeByGateway(Builder $query, string $gateway): void
    {
        $query->where('gateway', $gateway);
    }

    public function isCompleted(): bool
    {
        return $this->status === 'completed';
    }

    public function isFailed(): bool
    {
        return $this->status === 'failed';
    }
}

// app/Models/Order.php
class Order extends Model
{
    protected $fillable = [
        'order_number',
        'user_id',
        'total',
        'currency',
        'status',
    ];

    protected $casts = [
        'total' => 'decimal:2',
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function payments(): MorphMany
    {
        return $this->morphMany(Payment::class, 'payable');
    }

    public function scopePaid(Builder $query): void
    {
        $query->where('status', 'paid');
    }

    public function getFormattedTotalAttribute(): string
    {
        return number_format($this->total, 2);
    }

    public function isPaid(): bool
    {
        return $this->status === 'paid';
    }
}
```

## Contracts

```php
// app/Contracts/PaymentGatewayInterface.php
interface PaymentGatewayInterface
{
    public function charge(float $amount, string $currency, array $options = []): array;
    
    public function refund(string $transactionId, float $amount = null): array;
    
    public function getTransactionStatus(string $transactionId): string;
    
    public function getName(): string;
}
```

## Configuration

```php
// config/payment.php
return [
    'default_gateway' => env('PAYMENT_DEFAULT_GATEWAY', 'stripe'),
    
    'gateways' => [
        'stripe' => [
            'key' => env('STRIPE_KEY'),
            'secret' => env('STRIPE_SECRET'),
        ],
        'paypal' => [
            'client_id' => env('PAYPAL_CLIENT_ID'),
            'client_secret' => env('PAYPAL_CLIENT_SECRET'),
            'sandbox' => env('PAYPAL_SANDBOX', true),
        ],
    ],
    
    'currency' => env('PAYMENT_CURRENCY', 'USD'),
];
```