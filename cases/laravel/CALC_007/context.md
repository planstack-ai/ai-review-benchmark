# Existing Codebase

## Schema

```php
// Database: users
Schema::create('users', function (Blueprint $table) {
    $table->id();
    $table->string('email')->unique();
    $table->string('name');
    $table->boolean('premium_member')->default(false);
    $table->string('loyalty_tier')->default('bronze'); // bronze, silver, gold
    $table->boolean('points_suspended')->default(false);
    $table->timestamps();
});

// Database: orders
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->decimal('subtotal', 10, 2);
    $table->decimal('discount_amount', 10, 2)->default(0);
    $table->decimal('total', 10, 2); // subtotal - discount_amount
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
    protected $fillable = ['email', 'name', 'premium_member', 'loyalty_tier', 'points_suspended'];

    protected $casts = [
        'premium_member' => 'boolean',
        'points_suspended' => 'boolean',
    ];

    public function orders(): HasMany
    {
        return $this->hasMany(Order::class);
    }

    public function isPremiumMember(): bool
    {
        return $this->premium_member;
    }

    public function isPointsSuspended(): bool
    {
        return $this->points_suspended;
    }
}

class Order extends Model
{
    protected $fillable = ['user_id', 'subtotal', 'discount_amount', 'total', 'status'];

    protected $casts = [
        'subtotal' => 'decimal:2',
        'discount_amount' => 'decimal:2',
        'total' => 'decimal:2',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function isCancelled(): bool
    {
        return $this->status === 'cancelled';
    }

    public function scopeCompleted($query)
    {
        return $query->where('status', 'completed');
    }
}
```

## Business Rules

- Points should be earned based on the **actual amount paid** (total after discounts), not the pre-discount subtotal
- The `total` field represents the final amount after discounts
