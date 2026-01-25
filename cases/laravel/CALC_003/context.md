# Existing Codebase

## Schema

```php
// Database: orders
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->decimal('subtotal', 10, 2)->default(0);
    $table->decimal('tax_amount', 10, 2)->default(0);
    $table->decimal('discount_amount', 10, 2)->default(0);
    $table->decimal('total', 10, 2)->default(0);
    $table->string('currency')->default('USD');
    $table->timestamps();
});

// Database: order_items
Schema::create('order_items', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained()->onDelete('cascade');
    $table->foreignId('product_id')->constrained();
    $table->integer('quantity');
    $table->decimal('unit_price', 10, 2);
    $table->decimal('discount_percentage', 5, 2)->nullable();
    $table->timestamps();
});
```

## Models

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Order extends Model
{
    protected $fillable = ['user_id', 'subtotal', 'tax_amount', 'discount_amount', 'total', 'currency'];

    protected $casts = [
        'subtotal' => 'decimal:2',
        'tax_amount' => 'decimal:2',
        'discount_amount' => 'decimal:2',
        'total' => 'decimal:2',
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function orderItems(): HasMany
    {
        return $this->hasMany(OrderItem::class);
    }
}

class OrderItem extends Model
{
    protected $fillable = ['order_id', 'product_id', 'quantity', 'unit_price', 'discount_percentage'];

    protected $casts = [
        'unit_price' => 'decimal:2',
        'discount_percentage' => 'decimal:2',
    ];

    public function order(): BelongsTo
    {
        return $this->belongsTo(Order::class);
    }

    public function product(): BelongsTo
    {
        return $this->belongsTo(Product::class);
    }

    public function getSubtotalAttribute(): float
    {
        return $this->unit_price * $this->quantity;
    }
}
```
