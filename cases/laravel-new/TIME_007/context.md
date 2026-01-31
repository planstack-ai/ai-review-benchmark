# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_create_orders_table.php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->string('order_number')->unique();
    $table->decimal('total_amount', 10, 2);
    $table->enum('status', ['pending', 'processing', 'shipped', 'delivered', 'cancelled']);
    $table->date('order_date');
    $table->date('expected_delivery_date')->nullable();
    $table->integer('delivery_days')->default(5);
    $table->timestamps();
});

// database/migrations/2024_01_20_create_holidays_table.php
Schema::create('holidays', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->date('date');
    $table->boolean('is_active')->default(true);
    $table->timestamps();
});
```

## Models

```php
// app/Models/Order.php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Casts\Attribute;
use Carbon\Carbon;

class Order extends Model
{
    protected $fillable = [
        'order_number',
        'total_amount',
        'status',
        'order_date',
        'expected_delivery_date',
        'delivery_days'
    ];

    protected $casts = [
        'order_date' => 'date',
        'expected_delivery_date' => 'date',
        'total_amount' => 'decimal:2'
    ];

    public function scopePending($query)
    {
        return $query->where('status', 'pending');
    }

    public function scopeProcessing($query)
    {
        return $query->where('status', 'processing');
    }

    protected function orderNumber(): Attribute
    {
        return Attribute::make(
            get: fn (string $value) => strtoupper($value),
        );
    }

    public function isDelivered(): bool
    {
        return $this->status === 'delivered';
    }

    public function markAsProcessing(): void
    {
        $this->update(['status' => 'processing']);
    }
}

// app/Models/Holiday.php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Carbon\Carbon;

class Holiday extends Model
{
    protected $fillable = ['name', 'date', 'is_active'];

    protected $casts = [
        'date' => 'date',
        'is_active' => 'boolean'
    ];

    public function scopeActive($query)
    {
        return $query->where('is_active', true);
    }

    public function scopeInDateRange($query, Carbon $startDate, Carbon $endDate)
    {
        return $query->whereBetween('date', [$startDate, $endDate]);
    }

    public function scopeUpcoming($query)
    {
        return $query->where('date', '>=', now()->toDateString());
    }

    public static function getHolidayDates(Carbon $startDate, Carbon $endDate): array
    {
        return static::active()
            ->inDateRange($startDate, $endDate)
            ->pluck('date')
            ->map(fn ($date) => $date->toDateString())
            ->toArray();
    }
}
```