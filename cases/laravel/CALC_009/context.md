# Existing Codebase

## Schema

```php
// Database: customers
Schema::create('customers', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('email')->unique();
    $table->boolean('blocked')->default(false);
    $table->boolean('payment_overdue')->default(false);
    $table->boolean('loyalty_member')->default(false);
    $table->timestamps();
});

// Database: orders
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('customer_id')->nullable()->constrained();
    $table->foreignId('coupon_id')->nullable()->constrained();
    $table->decimal('discount_percentage', 5, 2)->nullable();
    $table->timestamps();
});

// Database: order_items
Schema::create('order_items', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained();
    $table->integer('quantity');
    $table->decimal('unit_price', 10, 2);
    $table->timestamps();
});
```

## Models

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Customer extends Model
{
    protected $fillable = ['name', 'email', 'blocked', 'payment_overdue', 'loyalty_member'];

    protected $casts = [
        'blocked' => 'boolean',
        'payment_overdue' => 'boolean',
        'loyalty_member' => 'boolean',
    ];

    public function isBlocked(): bool
    {
        return $this->blocked;
    }

    public function hasPaymentOverdue(): bool
    {
        return $this->payment_overdue;
    }

    public function isLoyaltyMember(): bool
    {
        return $this->loyalty_member;
    }
}

class Coupon extends Model
{
    protected $fillable = ['code', 'discount_amount', 'active'];

    protected $casts = [
        'discount_amount' => 'decimal:2',
        'active' => 'boolean',
    ];

    public function isActive(): bool
    {
        return $this->active;
    }
}
```

## Business Rules

- **Minimum order validation**: The minimum order amount check (1000 yen) should verify that the **final amount after all discounts** meets the threshold
- An order with 1500 yen subtotal and 600 yen discount should fail validation (900 yen final < 1000 yen minimum)
