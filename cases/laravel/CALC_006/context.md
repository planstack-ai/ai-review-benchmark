# Existing Codebase

## Schema

```php
// Database: orders
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->foreignId('shipping_address_id')->nullable()->constrained();
    $table->decimal('subtotal', 10, 2);
    $table->decimal('tax_amount', 10, 2)->default(0);
    $table->decimal('discount_amount', 10, 2)->default(0);
    $table->decimal('shipping_amount', 10, 2)->default(0);
    $table->string('shipping_method')->default('standard');
    $table->timestamps();
});

// Database: shipping_addresses
Schema::create('shipping_addresses', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->string('country')->default('JP');
    $table->string('prefecture');
    $table->string('city');
    $table->string('address_line');
    $table->string('postal_code');
    $table->timestamps();
});

// Database: products
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->decimal('price', 10, 2);
    $table->integer('weight')->default(0); // in grams
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
    protected $fillable = [
        'user_id', 'shipping_address_id', 'subtotal', 'tax_amount',
        'discount_amount', 'shipping_amount', 'shipping_method'
    ];

    public function lineItems(): HasMany
    {
        return $this->hasMany(LineItem::class);
    }

    public function shippingAddress(): BelongsTo
    {
        return $this->belongsTo(ShippingAddress::class);
    }
}

class LineItem extends Model
{
    protected $fillable = ['order_id', 'product_id', 'quantity', 'unit_price'];

    public function product(): BelongsTo
    {
        return $this->belongsTo(Product::class);
    }

    public function getTotalPriceAttribute(): float
    {
        return $this->quantity * $this->unit_price;
    }
}

class ShippingAddress extends Model
{
    protected $fillable = ['user_id', 'country', 'prefecture', 'city', 'address_line', 'postal_code'];
}
```

## Business Rules

- Free shipping threshold: Orders of 5000 yen **or more** qualify for free standard shipping
- This means orders of exactly 5000 yen should get free shipping
