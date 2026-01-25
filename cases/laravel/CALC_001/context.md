# Existing Codebase

## Schema

```php
// Database: users
Schema::create('users', function (Blueprint $table) {
    $table->id();
    $table->string('email')->unique();
    $table->string('name');
    $table->boolean('is_member')->default(false);
    $table->timestamps();
});

// Database: products
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->integer('price_cents');
    $table->boolean('active')->default(true);
    $table->timestamps();
});

// Database: orders
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->integer('total_cents');
    $table->integer('discount_cents')->default(0);
    $table->string('status')->default('pending');
    $table->timestamps();
});
```

## Models

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class User extends Model
{
    protected $fillable = ['email', 'name', 'is_member'];

    protected $casts = [
        'is_member' => 'boolean',
    ];

    public function orders(): HasMany
    {
        return $this->hasMany(Order::class);
    }

    public function scopeMembers($query)
    {
        return $query->where('is_member', true);
    }

    public function scopeNonMembers($query)
    {
        return $query->where('is_member', false);
    }

    public function isMember(): bool
    {
        return $this->is_member;
    }
}

class Product extends Model
{
    protected $fillable = ['name', 'price_cents', 'active'];

    protected $casts = [
        'active' => 'boolean',
    ];

    public function orderItems(): HasMany
    {
        return $this->hasMany(OrderItem::class);
    }

    public function scopeActive($query)
    {
        return $query->where('active', true);
    }

    public function getPriceAttribute(): float
    {
        return $this->price_cents / 100;
    }
}

class Order extends Model
{
    protected $fillable = ['user_id', 'total_cents', 'discount_cents', 'status'];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function orderItems(): HasMany
    {
        return $this->hasMany(OrderItem::class);
    }

    public function scopeConfirmed($query)
    {
        return $query->where('status', 'confirmed');
    }

    public function scopeWithDiscount($query)
    {
        return $query->where('discount_cents', '>', 0);
    }

    public function getSubtotalAttribute(): float
    {
        return $this->orderItems->sum(fn($item) => $item->quantity * $item->unit_price_cents) / 100;
    }

    public function getTotalAttribute(): float
    {
        return $this->total_cents / 100;
    }

    public function getDiscountAttribute(): float
    {
        return $this->discount_cents / 100;
    }

    public function getFinalAmountAttribute(): float
    {
        return $this->subtotal - $this->discount;
    }
}

class OrderItem extends Model
{
    protected $fillable = ['order_id', 'product_id', 'quantity', 'unit_price_cents'];

    public function order()
    {
        return $this->belongsTo(Order::class);
    }

    public function product()
    {
        return $this->belongsTo(Product::class);
    }

    public function getLineTotalAttribute(): float
    {
        return ($this->quantity * $this->unit_price_cents) / 100;
    }
}
```
