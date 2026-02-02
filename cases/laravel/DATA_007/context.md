# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_orders_table.php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('orders', function (Blueprint $table) {
            $table->id();
            $table->string('order_number')->unique();
            $table->foreignId('customer_id')->constrained();
            $table->enum('status', ['pending', 'processing', 'shipped', 'delivered', 'cancelled']);
            $table->decimal('total_amount', 10, 2);
            $table->timestamp('ordered_at');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('orders');
    }
};
```

```php
// database/migrations/2024_01_15_000002_create_order_items_table.php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('order_items', function (Blueprint $table) {
            $table->id();
            $table->foreignId('order_id')->constrained();
            $table->foreignId('product_id')->constrained();
            $table->integer('quantity');
            $table->decimal('unit_price', 8, 2);
            $table->decimal('total_price', 10, 2);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('order_items');
    }
};
```

## Models

```php
// app/Models/Order.php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Order extends Model
{
    use HasFactory;

    protected $fillable = [
        'order_number',
        'customer_id',
        'status',
        'total_amount',
        'ordered_at',
    ];

    protected $casts = [
        'total_amount' => 'decimal:2',
        'ordered_at' => 'datetime',
    ];

    public function customer(): BelongsTo
    {
        return $this->belongsTo(Customer::class);
    }

    public function items(): HasMany
    {
        return $this->hasMany(OrderItem::class);
    }

    public function scopeByStatus(Builder $query, string $status): Builder
    {
        return $query->where('status', $status);
    }

    public function scopeRecent(Builder $query): Builder
    {
        return $query->orderBy('ordered_at', 'desc');
    }

    public function getTotalItemsAttribute(): int
    {
        return $this->items->sum('quantity');
    }
}
```

```php
// app/Models/OrderItem.php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

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
        'quantity' => 'integer',
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

    protected static function booted(): void
    {
        static::saving(function (OrderItem $orderItem) {
            $orderItem->total_price = $orderItem->quantity * $orderItem->unit_price;
        });
    }
}
```

```php
// app/Models/Customer.php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Customer extends Model
{
    use HasFactory;

    protected $fillable = [
        'name',
        'email',
        'phone',
    ];

    public function orders(): HasMany
    {
        return $this->hasMany(Order::class);
    }
}
```