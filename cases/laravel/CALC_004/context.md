# Existing Codebase

## Schema

```php
// Database: products
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->decimal('price', 10, 2);
    $table->boolean('active')->default(true);
    $table->timestamps();
});

// Database: discount_codes
Schema::create('discount_codes', function (Blueprint $table) {
    $table->id();
    $table->string('code')->unique();
    $table->decimal('discount_percentage', 5, 2);
    $table->boolean('active')->default(true);
    $table->timestamp('expires_at')->nullable();
    $table->timestamps();
});
```

## Models

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Product extends Model
{
    protected $fillable = ['name', 'price', 'active'];

    protected $casts = [
        'price' => 'decimal:2',
        'active' => 'boolean',
    ];

    public function scopeActive($query)
    {
        return $query->where('active', true);
    }
}

class DiscountCode extends Model
{
    protected $fillable = ['code', 'discount_percentage', 'active', 'expires_at'];

    protected $casts = [
        'discount_percentage' => 'decimal:2',
        'active' => 'boolean',
        'expires_at' => 'datetime',
    ];

    public function isValid(): bool
    {
        return $this->active && (!$this->expires_at || $this->expires_at->isFuture());
    }
}
```
