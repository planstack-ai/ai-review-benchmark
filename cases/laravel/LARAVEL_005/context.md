# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_orders_table.php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->string('order_number')->unique();
    $table->foreignId('user_id')->constrained();
    $table->enum('status', ['pending', 'processing', 'shipped', 'delivered', 'cancelled']);
    $table->decimal('total_amount', 10, 2);
    $table->timestamp('shipped_at')->nullable();
    $table->timestamps();
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

// database/migrations/2024_01_15_000003_create_jobs_table.php
Schema::create('jobs', function (Blueprint $table) {
    $table->bigIncrements('id');
    $table->string('queue')->index();
    $table->longText('payload');
    $table->unsignedTinyInteger('attempts');
    $table->unsignedInteger('reserved_at')->nullable();
    $table->unsignedInteger('available_at');
    $table->unsignedInteger('created_at');
    $table->index(['queue', 'reserved_at']);
});
```

## Models

```php
// app/Models/User.php
class User extends Authenticatable
{
    use HasFactory, Notifiable;

    protected $fillable = [
        'name',
        'email',
        'password',
    ];

    protected $hidden = [
        'password',
        'remember_token',
    ];

    public function orders(): HasMany
    {
        return $this->hasMany(Order::class);
    }

    public function preferredNotificationChannel(): string
    {
        return $this->notification_preferences['order_updates'] ?? 'mail';
    }
}

// app/Models/Order.php
class Order extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'order_number',
        'status',
        'total_amount',
        'shipped_at',
    ];

    protected $casts = [
        'total_amount' => 'decimal:2',
        'shipped_at' => 'datetime',
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function items(): HasMany
    {
        return $this->hasMany(OrderItem::class);
    }

    public function scopeRecent(Builder $query): Builder
    {
        return $query->where('created_at', '>=', now()->subDays(30));
    }

    public function scopeByStatus(Builder $query, string $status): Builder
    {
        return $query->where('status', $status);
    }

    public function isProcessing(): bool
    {
        return $this->status === 'processing';
    }

    public function isPending(): bool
    {
        return $this->status === 'pending';
    }

    protected static function booted(): void
    {
        static::creating(function (Order $order) {
            $order->order_number = 'ORD-' . strtoupper(Str::random(8));
        });
    }
}

// app/Models/OrderItem.php
class OrderItem extends Model
{
    use HasFactory;

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
```