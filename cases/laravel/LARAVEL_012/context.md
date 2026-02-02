# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_products_table.php
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('sku')->unique();
    $table->decimal('price', 10, 2);
    $table->integer('stock_quantity')->default(0);
    $table->boolean('track_inventory')->default(true);
    $table->timestamps();
});

// database/migrations/2024_01_15_000002_create_orders_table.php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->string('order_number')->unique();
    $table->foreignId('user_id')->constrained();
    $table->enum('status', ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']);
    $table->decimal('total_amount', 10, 2);
    $table->timestamps();
});

// database/migrations/2024_01_15_000003_create_order_items_table.php
Schema::create('order_items', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained()->onDelete('cascade');
    $table->foreignId('product_id')->constrained();
    $table->integer('quantity');
    $table->decimal('unit_price', 10, 2);
    $table->decimal('total_price', 10, 2);
    $table->timestamps();
});
```

## Models

```php
// app/Models/Product.php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Product extends Model
{
    protected $fillable = [
        'name',
        'sku',
        'price',
        'stock_quantity',
        'track_inventory',
    ];

    protected $casts = [
        'price' => 'decimal:2',
        'track_inventory' => 'boolean',
    ];

    public function orderItems(): HasMany
    {
        return $this->hasMany(OrderItem::class);
    }

    public function scopeInStock($query)
    {
        return $query->where('stock_quantity', '>', 0);
    }

    public function scopeTracked($query)
    {
        return $query->where('track_inventory', true);
    }

    public function hasStock(int $quantity): bool
    {
        return !$this->track_inventory || $this->stock_quantity >= $quantity;
    }

    public function decrementStock(int $quantity): bool
    {
        if (!$this->track_inventory) {
            return true;
        }

        return $this->decrement('stock_quantity', $quantity) > 0;
    }
}

// app/Models/Order.php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Order extends Model
{
    protected $fillable = [
        'order_number',
        'user_id',
        'status',
        'total_amount',
    ];

    protected $casts = [
        'total_amount' => 'decimal:2',
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function items(): HasMany
    {
        return $this->hasMany(OrderItem::class);
    }

    public function scopeConfirmed($query)
    {
        return $query->where('status', 'confirmed');
    }
}

// app/Models/OrderItem.php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

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
```