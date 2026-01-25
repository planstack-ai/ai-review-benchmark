# Existing Codebase

## Schema

```php
// Database: coupons
Schema::create('coupons', function (Blueprint $table) {
    $table->id();
    $table->string('code')->unique();
    $table->enum('discount_type', ['percentage', 'fixed_amount']);
    $table->decimal('discount_value', 10, 2);
    $table->decimal('minimum_order_amount', 10, 2)->nullable();
    $table->integer('usage_limit')->nullable();
    $table->integer('usage_count')->default(0);
    $table->boolean('active')->default(true);
    $table->timestamp('expires_at')->nullable();
    $table->timestamps();
});

// Database: orders
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->decimal('subtotal', 10, 2);
    $table->decimal('coupon_discount', 10, 2)->default(0);
    $table->decimal('tax_amount', 10, 2)->default(0);
    $table->decimal('shipping_amount', 10, 2)->default(0);
    $table->decimal('total', 10, 2);
    $table->timestamps();
});

// Database: coupon_usages
Schema::create('coupon_usages', function (Blueprint $table) {
    $table->id();
    $table->foreignId('coupon_id')->constrained();
    $table->foreignId('order_id')->constrained();
    $table->decimal('discount_amount', 10, 2);
    $table->timestamp('used_at');
    $table->timestamps();
});
```

## Models

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Carbon\Carbon;

class Coupon extends Model
{
    protected $fillable = [
        'code', 'discount_type', 'discount_value', 'minimum_order_amount',
        'usage_limit', 'usage_count', 'active', 'expires_at'
    ];

    protected $casts = [
        'discount_value' => 'decimal:2',
        'minimum_order_amount' => 'decimal:2',
        'active' => 'boolean',
        'expires_at' => 'datetime',
    ];

    public function isActive(): bool
    {
        return $this->active;
    }

    public function isExpired(): bool
    {
        return $this->expires_at && $this->expires_at->isPast();
    }
}

class Order extends Model
{
    protected $fillable = [
        'user_id', 'subtotal', 'coupon_discount', 'tax_amount',
        'shipping_amount', 'total'
    ];

    public function appliedCoupons(): BelongsToMany
    {
        return $this->belongsToMany(Coupon::class, 'coupon_usages')
            ->withPivot('discount_amount', 'used_at');
    }

    public function hasCouponApplied(): bool
    {
        return $this->coupon_discount > 0;
    }
}
```

## Business Rules

- **Single coupon policy**: Only one coupon can be applied per order
- If an order already has a coupon applied, additional coupons must be rejected
