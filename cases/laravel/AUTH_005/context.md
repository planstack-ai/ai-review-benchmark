# Existing Codebase

## Schema

```php
// Database: users
Schema::create('users', function (Blueprint $table) {
    $table->id();
    $table->string('email')->unique();
    $table->boolean('is_member')->default(false);
    $table->timestamps();
});

// Database: products
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->decimal('regular_price', 10, 2);
    $table->decimal('member_price', 10, 2)->nullable();
    $table->boolean('member_pricing_enabled')->default(false);
    $table->boolean('quantity_discounts_enabled')->default(false);
    $table->timestamps();
});
```

## Models

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Authenticatable
{
    protected $fillable = ['email', 'is_member'];

    protected $casts = [
        'is_member' => 'boolean',
    ];

    public function isMember(): bool
    {
        return $this->is_member;
    }
}

class Product extends Model
{
    protected $fillable = [
        'name', 'regular_price', 'member_price',
        'member_pricing_enabled', 'quantity_discounts_enabled'
    ];

    protected $casts = [
        'member_pricing_enabled' => 'boolean',
        'quantity_discounts_enabled' => 'boolean',
    ];

    public function hasMemberPricingEnabled(): bool
    {
        return $this->member_pricing_enabled;
    }

    public function hasQuantityDiscountsEnabled(): bool
    {
        return $this->quantity_discounts_enabled;
    }
}
```

## Pricing Logic Requirement

Member pricing should ONLY apply when:
1. Product has member pricing enabled
2. User is logged in (not null)
3. User has member status (is_member = true)

```php
// Correct check
if ($user && $user->isMember() && $product->hasMemberPricingEnabled()) {
    return $product->member_price;
}
return $product->regular_price;
```
