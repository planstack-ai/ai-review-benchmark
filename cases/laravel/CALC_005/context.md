# Existing Codebase

## Schema

```php
// Database: tax_rates
Schema::create('tax_rates', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->decimal('rate', 5, 4); // e.g., 0.1000 for 10%
    $table->boolean('is_current')->default(false);
    $table->timestamp('effective_from');
    $table->timestamps();
});

// Database: products
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('category');
    $table->decimal('price', 10, 2);
    $table->integer('weight')->default(0);
    $table->boolean('on_sale')->default(false);
    $table->decimal('sale_percentage', 5, 2)->default(0);
    $table->boolean('bulk_discount_eligible')->default(false);
    $table->timestamps();
});
```

## Models

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class TaxRate extends Model
{
    protected $fillable = ['name', 'rate', 'is_current', 'effective_from'];

    protected $casts = [
        'rate' => 'decimal:4',
        'is_current' => 'boolean',
        'effective_from' => 'datetime',
    ];

    public static function current(): float
    {
        // Current tax rate is 10% (0.10)
        return static::where('is_current', true)->first()?->rate ?? 0.10;
    }
}

class Customer extends Model
{
    protected $fillable = ['name', 'email', 'tax_exempt'];

    protected $casts = [
        'tax_exempt' => 'boolean',
    ];

    public function isTaxExempt(): bool
    {
        return $this->tax_exempt;
    }
}

class ShippingAddress extends Model
{
    protected $fillable = ['customer_id', 'street', 'city', 'state', 'country', 'zip'];

    public function getFullAddressAttribute(): string
    {
        return "{$this->street}, {$this->city}, {$this->state} {$this->zip}";
    }
}
```

## Current Tax Rate Configuration

The system was recently updated to use 10% tax rate. The TaxRate::current() method returns the current rate from the database.
