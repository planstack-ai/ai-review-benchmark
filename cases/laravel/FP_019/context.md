# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_categories_table.php
Schema::create('categories', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('slug')->unique();
    $table->boolean('is_active')->default(true);
    $table->timestamps();
});

// database/migrations/2024_01_15_000002_create_products_table.php
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->foreignId('category_id')->constrained();
    $table->string('name');
    $table->string('slug')->unique();
    $table->text('description');
    $table->decimal('price', 10, 2);
    $table->integer('stock_quantity')->default(0);
    $table->boolean('is_active')->default(true);
    $table->timestamps();
    
    $table->index(['category_id', 'is_active']);
    $table->index(['price', 'is_active']);
});

// database/migrations/2024_01_15_000003_create_product_reviews_table.php
Schema::create('product_reviews', function (Blueprint $table) {
    $table->id();
    $table->foreignId('product_id')->constrained();
    $table->foreignId('user_id')->constrained();
    $table->tinyInteger('rating')->unsigned();
    $table->text('comment')->nullable();
    $table->boolean('is_approved')->default(false);
    $table->timestamps();
    
    $table->index(['product_id', 'is_approved']);
    $table->unique(['product_id', 'user_id']);
});
```

## Models

```php
// app/Models/Category.php
class Category extends Model
{
    protected $fillable = ['name', 'slug', 'is_active'];

    protected function casts(): array
    {
        return [
            'is_active' => 'boolean',
        ];
    }

    public function products(): HasMany
    {
        return $this->hasMany(Product::class);
    }

    public function scopeActive(Builder $query): void
    {
        $query->where('is_active', true);
    }
}

// app/Models/Product.php
class Product extends Model
{
    protected $fillable = [
        'category_id', 'name', 'slug', 'description', 
        'price', 'stock_quantity', 'is_active'
    ];

    protected function casts(): array
    {
        return [
            'price' => 'decimal:2',
            'is_active' => 'boolean',
        ];
    }

    public function category(): BelongsTo
    {
        return $this->belongsTo(Category::class);
    }

    public function reviews(): HasMany
    {
        return $this->hasMany(ProductReview::class);
    }

    public function approvedReviews(): HasMany
    {
        return $this->reviews()->where('is_approved', true);
    }

    public function scopeActive(Builder $query): void
    {
        $query->where('is_active', true);
    }

    public function scopeInStock(Builder $query): void
    {
        $query->where('stock_quantity', '>', 0);
    }

    public function scopeByPriceRange(Builder $query, float $min, float $max): void
    {
        $query->whereBetween('price', [$min, $max]);
    }
}

// app/Models/ProductReview.php
class ProductReview extends Model
{
    protected $fillable = ['product_id', 'user_id', 'rating', 'comment', 'is_approved'];

    protected function casts(): array
    {
        return [
            'is_approved' => 'boolean',
        ];
    }

    public function product(): BelongsTo
    {
        return $this->belongsTo(Product::class);
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function scopeApproved(Builder $query): void
    {
        $query->where('is_approved', true);
    }
}
```