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
    $table->string('idempotency_key')->unique()->nullable();
    $table->json('metadata')->nullable();
    $table->timestamps();
    
    $table->index(['user_id', 'status']);
    $table->index('idempotency_key');
});

// database/migrations/2024_01_15_000002_create_order_items_table.php
Schema::create('order_items', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained()->cascadeOnDelete();
    $table->foreignId('product_id')->constrained();
    $table->integer('quantity');
    $table->decimal('unit_price', 8, 2);
    $table->decimal('total_price', 10, 2);
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
        'idempotency_key',
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

    public function items(): HasMany
    {
        return $this->hasMany(OrderItem::class);
    }

    public function scopeByIdempotencyKey(Builder $query, string $key): Builder
    {
        return $query->where('idempotency_key', $key);
    }

    public function scopeForUser(Builder $query, int $userId): Builder
    {
        return $query->where('user_id', $userId);
    }

    public function scopeCompleted(Builder $query): Builder
    {
        return $query->where('status', 'completed');
    }

    public function isCompleted(): bool
    {
        return $this->status === 'completed';
    }

    public function isPending(): bool
    {
        return $this->status === 'pending';
    }

    protected static function boot(): void
    {
        parent::boot();
        
        static::creating(function (Order $order) {
            if (empty($order->order_number)) {
                $order->order_number = 'ORD-' . strtoupper(Str::random(8));
            }
        });
    }
}

// app/Models/OrderItem.php
class OrderItem extends Model
{
    protected $fillable = [
        'order_id',
        'product_id',
        'quantity',
        'unit_price',
        'total_price',
    ];

    protected $casts = [
        'unit_price' => 'decimal:2',
        'total_price' => 'decimal:2',
    ];

    public function order(): BelongsTo
    {
        return $this->belongsTo(Order::class);
    }

    public function product(): BelongsTo
    {
        return $this->belongsTo(Product::class);
    }
}

// app/Models/Product.php
class Product extends Model
{
    protected $fillable = ['name', 'price', 'stock_quantity'];

    protected $casts = [
        'price' => 'decimal:2',
    ];

    public function orderItems(): HasMany
    {
        return $this->hasMany(OrderItem::class);
    }

    public function scopeInStock(Builder $query): Builder
    {
        return $query->where('stock_quantity', '>', 0);
    }

    public function hasStock(int $quantity): bool
    {
        return $this->stock_quantity >= $quantity;
    }
}
```