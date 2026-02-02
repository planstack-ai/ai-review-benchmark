# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_orders_table.php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->string('order_number')->unique();
    $table->foreignId('customer_id')->constrained();
    $table->enum('status', ['pending', 'processing', 'shipped', 'delivered', 'cancelled']);
    $table->decimal('total_amount', 10, 2);
    $table->timestamp('order_date');
    $table->timestamps();
});

// database/migrations/2024_01_15_000002_create_order_items_table.php
Schema::create('order_items', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained()->onDelete('cascade');
    $table->foreignId('product_id')->constrained();
    $table->string('product_name');
    $table->integer('quantity');
    $table->decimal('unit_price', 8, 2);
    $table->decimal('total_price', 10, 2);
    $table->enum('status', ['active', 'cancelled', 'refunded']);
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
        'customer_id',
        'status',
        'total_amount',
        'order_date',
    ];

    protected $casts = [
        'order_date' => 'datetime',
        'total_amount' => 'decimal:2',
    ];

    public function items(): HasMany
    {
        return $this->hasMany(OrderItem::class);
    }

    public function customer(): BelongsTo
    {
        return $this->belongsTo(Customer::class);
    }

    public function scopeCompleted(Builder $query): void
    {
        $query->whereIn('status', ['shipped', 'delivered']);
    }

    public function scopeActive(Builder $query): void
    {
        $query->whereNotIn('status', ['cancelled']);
    }
}

// app/Models/OrderItem.php
class OrderItem extends Model
{
    protected $fillable = [
        'order_id',
        'product_id',
        'product_name',
        'quantity',
        'unit_price',
        'total_price',
        'status',
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

    public function scopeActive(Builder $query): void
    {
        $query->where('status', 'active');
    }

    public function scopeHighValue(Builder $query): void
    {
        $query->where('total_price', '>=', 100);
    }

    public function scopeByPriceRange(Builder $query, float $min, float $max): void
    {
        $query->whereBetween('total_price', [$min, $max]);
    }

    public function getIsExpensiveAttribute(): bool
    {
        return $this->total_price >= 50;
    }
}

// app/Models/Product.php
class Product extends Model
{
    protected $fillable = ['name', 'price', 'category_id'];

    protected $casts = [
        'price' => 'decimal:2',
    ];

    public function orderItems(): HasMany
    {
        return $this->hasMany(OrderItem::class);
    }
}
```