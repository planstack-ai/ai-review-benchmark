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
            $table->foreignId('category_id')->constrained();
            $table->boolean('is_active')->default(true);
            $table->timestamps();
            
            $table->index(['category_id', 'is_active']);
            $table->index('created_at');
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
            $table->text('description')->nullable();
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
        'category_id',
        'is_active',
    ];

    protected $casts = [
        'price' => 'decimal:2',
        'stock_quantity' => 'integer',
        'is_active' => 'boolean',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    public const BATCH_SIZE = 1000;
    public const MAX_BATCH_SIZE = 5000;

    public function category(): BelongsTo
    {
        return $this->belongsTo(Category::class);
    }

    public function scopeActive(Builder $query): Builder
    {
        return $query->where('is_active', true);
    }

    public function scopeInStock(Builder $query): Builder
    {
        return $query->where('stock_quantity', '>', 0);
    }

    public function scopeByCategory(Builder $query, int $categoryId): Builder
    {
        return $query->where('category_id', $categoryId);
    }

    public function getFormattedPriceAttribute(): string
    {
        return '$' . number_format($this->price, 2);
    }

    protected static function booted(): void
    {
        static::creating(function (Product $product) {
            if (empty($product->created_at)) {
                $product->created_at = now();
            }
            if (empty($product->updated_at)) {
                $product->updated_at = now();
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
        'description',
        'is_active',
    ];

    protected $casts = [
        'is_active' => 'boolean',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
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