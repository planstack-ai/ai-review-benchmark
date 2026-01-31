# Existing Codebase

## Schema

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('orders', function (Blueprint $table) {
            $table->id();
            $table->string('order_number')->unique();
            $table->foreignId('customer_id')->constrained();
            $table->decimal('total_amount', 10, 2);
            $table->date('delivery_date');
            $table->enum('status', ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled'])
                  ->default('pending');
            $table->timestamps();
            
            $table->index(['delivery_date', 'status']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('orders');
    }
};
```

## Models

```php
<?php

namespace App\Models;

use Carbon\Carbon;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Order extends Model
{
    use HasFactory;

    protected $fillable = [
        'order_number',
        'customer_id',
        'total_amount',
        'delivery_date',
        'status',
    ];

    protected $casts = [
        'delivery_date' => 'date',
        'total_amount' => 'decimal:2',
    ];

    public function customer(): BelongsTo
    {
        return $this->belongsTo(Customer::class);
    }

    public function scopeActive(Builder $query): void
    {
        $query->whereNotIn('status', ['cancelled']);
    }

    public function scopeUpcoming(Builder $query): void
    {
        $query->where('delivery_date', '>=', now()->toDateString());
    }

    public function scopePending(Builder $query): void
    {
        $query->where('status', 'pending');
    }

    public function getIsOverdueAttribute(): bool
    {
        return $this->delivery_date->isPast() && 
               in_array($this->status, ['pending', 'confirmed']);
    }

    public function getDaysUntilDeliveryAttribute(): int
    {
        return now()->diffInDays($this->delivery_date, false);
    }
}
```

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Customer extends Model
{
    use HasFactory;

    protected $fillable = [
        'name',
        'email',
        'phone',
        'address',
    ];

    public function orders(): HasMany
    {
        return $this->hasMany(Order::class);
    }

    public function activeOrders(): HasMany
    {
        return $this->orders()->active();
    }
}
```