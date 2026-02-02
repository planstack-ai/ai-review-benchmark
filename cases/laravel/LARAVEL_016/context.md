# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_orders_table.php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->string('order_number')->unique();
    $table->decimal('total_amount', 10, 2);
    $table->timestamp('order_date');
    $table->timestamp('delivery_date')->nullable();
    $table->enum('status', ['pending', 'processing', 'shipped', 'delivered', 'cancelled']);
    $table->string('shipping_method');
    $table->json('shipping_address');
    $table->timestamps();
});

// database/migrations/2024_01_15_000002_create_shipping_methods_table.php
Schema::create('shipping_methods', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('code')->unique();
    $table->integer('delivery_days');
    $table->boolean('skip_weekends')->default(false);
    $table->json('excluded_dates')->nullable();
    $table->boolean('active')->default(true);
    $table->timestamps();
});
```

## Models

```php
// app/Models/Order.php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Carbon\Carbon;

class Order extends Model
{
    protected $fillable = [
        'order_number',
        'total_amount',
        'order_date',
        'delivery_date',
        'status',
        'shipping_method',
        'shipping_address',
    ];

    protected $casts = [
        'order_date' => 'datetime',
        'delivery_date' => 'datetime',
        'total_amount' => 'decimal:2',
        'shipping_address' => 'array',
    ];

    public function shippingMethodDetails(): BelongsTo
    {
        return $this->belongsTo(ShippingMethod::class, 'shipping_method', 'code');
    }

    public function scopePending($query)
    {
        return $query->where('status', 'pending');
    }

    public function scopeDeliveredBetween($query, Carbon $start, Carbon $end)
    {
        return $query->whereBetween('delivery_date', [$start, $end]);
    }

    public function isOverdue(): bool
    {
        return $this->delivery_date && 
               $this->delivery_date->isPast() && 
               $this->status !== 'delivered';
    }
}

// app/Models/ShippingMethod.php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class ShippingMethod extends Model
{
    protected $fillable = [
        'name',
        'code',
        'delivery_days',
        'skip_weekends',
        'excluded_dates',
        'active',
    ];

    protected $casts = [
        'skip_weekends' => 'boolean',
        'excluded_dates' => 'array',
        'active' => 'boolean',
    ];

    public function orders(): HasMany
    {
        return $this->hasMany(Order::class, 'shipping_method', 'code');
    }

    public function scopeActive($query)
    {
        return $query->where('active', true);
    }

    public function getExcludedDatesCollection(): array
    {
        return collect($this->excluded_dates ?? [])
            ->map(fn($date) => \Carbon\Carbon::parse($date))
            ->toArray();
    }
}
```