# Existing Codebase

## Schema

```php
// Database: users
Schema::create('users', function (Blueprint $table) {
    $table->id();
    $table->string('email')->unique();
    $table->string('name');
    $table->string('role')->default('user'); // user, admin
    $table->timestamps();
});

// Database: products
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->decimal('price', 10, 2);
    $table->timestamp('price_updated_at')->nullable();
    $table->foreignId('price_updated_by')->nullable()->constrained('users');
    $table->timestamps();
});

// Database: price_histories
Schema::create('price_histories', function (Blueprint $table) {
    $table->id();
    $table->foreignId('product_id')->constrained();
    $table->decimal('old_price', 10, 2);
    $table->decimal('new_price', 10, 2);
    $table->foreignId('changed_by')->constrained('users');
    $table->text('reason');
    $table->timestamp('changed_at');
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
    protected $fillable = ['name', 'email', 'role'];

    public function isAdmin(): bool
    {
        return $this->role === 'admin';
    }
}

class Product extends Model
{
    protected $fillable = ['name', 'price', 'price_updated_at', 'price_updated_by'];

    public function priceHistories()
    {
        return $this->hasMany(PriceHistory::class);
    }
}
```

## Authorization Requirement

Price updates are a privileged operation:
```php
// REQUIRED check before any price update
if (!$user->isAdmin()) {
    throw new AuthorizationException('Only admins can update prices');
}
```
