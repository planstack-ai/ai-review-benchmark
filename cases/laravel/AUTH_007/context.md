# Existing Codebase

## Schema

```php
// Database: coupons
Schema::create('coupons', function (Blueprint $table) {
    $table->id();
    $table->string('code')->unique();
    $table->foreignId('user_id')->nullable()->constrained(); // null = global, set = user-specific
    $table->enum('discount_type', ['percentage', 'fixed_amount']);
    $table->decimal('discount_value', 10, 2);
    $table->decimal('minimum_order_amount', 10, 2)->nullable();
    $table->decimal('max_discount_amount', 10, 2)->nullable();
    $table->integer('usage_limit')->nullable();
    $table->boolean('active')->default(true);
    $table->timestamp('expires_at')->nullable();
    $table->timestamps();
});

// Database: coupon_usages
Schema::create('coupon_usages', function (Blueprint $table) {
    $table->id();
    $table->foreignId('coupon_id')->constrained();
    $table->foreignId('user_id')->constrained();
    $table->decimal('discount_amount', 10, 2);
    $table->decimal('order_total', 10, 2);
    $table->timestamp('used_at');
    $table->timestamps();
});
```

## Models

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Coupon extends Model
{
    protected $fillable = [
        'code', 'user_id', 'discount_type', 'discount_value',
        'minimum_order_amount', 'max_discount_amount',
        'usage_limit', 'active', 'expires_at'
    ];

    protected $casts = [
        'active' => 'boolean',
        'expires_at' => 'datetime',
    ];

    // Relationship to owning user (if user-specific)
    public function owner()
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    public function usages()
    {
        return $this->hasMany(CouponUsage::class);
    }

    public function isGlobal(): bool
    {
        return $this->user_id === null;
    }

    public function isOwnedBy(User $user): bool
    {
        return $this->user_id === $user->id;
    }
}
```

## Coupon Ownership Rules

- **Global coupons**: `user_id = null` - can be used by any user
- **User-specific coupons**: `user_id` set - can ONLY be used by that specific user

Validation required:
```php
if (!$coupon->isGlobal() && !$coupon->isOwnedBy($user)) {
    throw new UnauthorizedException('This coupon is not valid for your account');
}
```
