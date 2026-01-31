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
        Schema::create('products', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('sku')->unique();
            $table->decimal('price', 10, 2);
            $table->integer('stock_quantity')->default(0);
            $table->boolean('is_active')->default(true);
            $table->foreignId('category_id')->constrained();
            $table->timestamp('last_restocked_at')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('products');
    }
};
```

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('categories', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('slug')->unique();
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('categories');
    }
};
```

## Models

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Builder;
use Carbon\Carbon;

class Product extends Model
{
    use HasFactory;

    protected $fillable = [
        'name',
        'sku',
        'price',
        'stock_quantity',
        'is_active',
        'category_id',
        'last_restocked_at',
    ];

    protected $casts = [
        'price' => 'decimal:2',
        'is_active' => 'boolean',
        'last_restocked_at' => 'datetime',
    ];

    public const LOW_STOCK_THRESHOLD = 10;
    public const OUT_OF_STOCK_THRESHOLD = 0;

    public function category(): BelongsTo
    {
        return $this->belongsTo(Category::class);
    }

    public function scopeActive(Builder $query): Builder
    {
        return $query->where('is_active', true);
    }

    public function scopeLowStock(Builder $query): Builder
    {
        return $query->where('stock_quantity', '<=', self::LOW_STOCK_THRESHOLD)
                    ->where('stock_quantity', '>', self::OUT_OF_STOCK_THRESHOLD);
    }

    public function scopeOutOfStock(Builder $query): Builder
    {
        return $query->where('stock_quantity', '<=', self::OUT_OF_STOCK_THRESHOLD);
    }

    public function scopeInCategory(Builder $query, int $categoryId): Builder
    {
        return $query->where('category_id', $categoryId);
    }

    public function getIsLowStockAttribute(): bool
    {
        return $this->stock_quantity <= self::LOW_STOCK_THRESHOLD 
               && $this->stock_quantity > self::OUT_OF_STOCK_THRESHOLD;
    }

    public function getIsOutOfStockAttribute(): bool
    {
        return $this->stock_quantity <= self::OUT_OF_STOCK_THRESHOLD;
    }

    protected static function booted(): void
    {
        static::updating(function (Product $product) {
            if ($product->isDirty('stock_quantity') && $product->stock_quantity > 0) {
                $product->last_restocked_at = now();
            }
        });
    }
}
```

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Builder;

class Category extends Model
{
    use HasFactory;

    protected $fillable = [
        'name',
        'slug',
        'is_active',
    ];

    protected $casts = [
        'is_active' => 'boolean',
    ];

    public function products(): HasMany
    {
        return $this->hasMany(Product::class);
    }

    public function activeProducts(): HasMany
    {
        return $this->products()->active();
    }

    public function scopeActive(Builder $query): Builder
    {
        return $query->where('is_active', true);
    }
}
```