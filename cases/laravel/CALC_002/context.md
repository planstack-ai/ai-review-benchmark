# Existing Codebase

## Schema

```php
// Database: orders
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->decimal('subtotal', 10, 2);
    $table->decimal('tax_amount', 10, 2)->default(0);
    $table->decimal('discount_amount', 10, 2)->default(0);
    $table->decimal('total', 10, 2);
    $table->string('currency')->default('USD');
    $table->timestamps();
});

// Database: line_items
Schema::create('line_items', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained()->onDelete('cascade');
    $table->foreignId('product_id')->constrained();
    $table->integer('quantity');
    $table->decimal('unit_price', 10, 2);
    $table->timestamps();
});

// Database: discount_codes
Schema::create('discount_codes', function (Blueprint $table) {
    $table->id();
    $table->string('code')->unique();
    $table->enum('discount_type', ['percentage', 'fixed']);
    $table->decimal('value', 10, 2);
    $table->boolean('active')->default(true);
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

    public function lineItems(): HasMany
    {
        return $this->hasMany(LineItem::class);
    }

    public function discountCode(): BelongsTo
    {
        return $this->belongsTo(DiscountCode::class);
    }
}

class LineItem extends Model
{
    protected $fillable = ['order_id', 'product_id', 'quantity', 'unit_price'];

    protected $casts = [
        'unit_price' => 'decimal:2',
    ];

    public function order(): BelongsTo
    {
        return $this->belongsTo(Order::class);
    }

    public function product(): BelongsTo
    {
        return $this->belongsTo(Product::class);
    }

    public function getTotalPriceAttribute(): float
    {
        return $this->quantity * $this->unit_price;
    }
}

class DiscountCode extends Model
{
    protected $fillable = ['code', 'discount_type', 'value', 'active'];

    protected $casts = [
        'value' => 'decimal:2',
        'active' => 'boolean',
    ];
}
```
