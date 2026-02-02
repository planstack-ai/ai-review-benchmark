# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_products_table.php
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->decimal('base_price', 10, 2);
    $table->boolean('taxable')->default(true);
    $table->timestamps();
});

// database/migrations/2024_01_15_000002_create_customers_table.php
Schema::create('customers', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('email')->unique();
    $table->enum('tier', ['bronze', 'silver', 'gold', 'platinum'])->default('bronze');
    $table->decimal('discount_percentage', 5, 2)->default(0);
    $table->timestamps();
});

// database/migrations/2024_01_15_000003_create_quantity_discounts_table.php
Schema::create('quantity_discounts', function (Blueprint $table) {
    $table->id();
    $table->foreignId('product_id')->constrained()->cascadeOnDelete();
    $table->integer('min_quantity');
    $table->decimal('discount_percentage', 5, 2);
    $table->timestamps();
});

// database/migrations/2024_01_15_000004_create_promotions_table.php
Schema::create('promotions', function (Blueprint $table) {
    $table->id();
    $table->string('code')->unique();
    $table->decimal('discount_percentage', 5, 2);
    $table->boolean('applies_to_discounted_price')->default(false);
    $table->datetime('starts_at');
    $table->datetime('expires_at');
    $table->timestamps();
});
```

## Models

```php
// app/Models/Product.php
class Product extends Model
{
    protected $fillable = ['name', 'base_price', 'taxable'];

    protected $casts = [
        'base_price' => 'decimal:2',
        'taxable' => 'boolean',
    ];

    public function quantityDiscounts(): HasMany
    {
        return $this->hasMany(QuantityDiscount::class)->orderBy('min_quantity');
    }

    public function getApplicableQuantityDiscount(int $quantity): ?QuantityDiscount
    {
        return $this->quantityDiscounts()
            ->where('min_quantity', '<=', $quantity)
            ->orderByDesc('min_quantity')
            ->first();
    }
}

// app/Models/Customer.php
class Customer extends Model
{
    protected $fillable = ['name', 'email', 'tier', 'discount_percentage'];

    protected $casts = [
        'discount_percentage' => 'decimal:2',
        'tier' => CustomerTier::class,
    ];

    public function scopeEligibleForDiscount(Builder $query): void
    {
        $query->where('discount_percentage', '>', 0);
    }
}

// app/Models/QuantityDiscount.php
class QuantityDiscount extends Model
{
    protected $fillable = ['product_id', 'min_quantity', 'discount_percentage'];

    protected $casts = [
        'discount_percentage' => 'decimal:2',
    ];

    public function product(): BelongsTo
    {
        return $this->belongsTo(Product::class);
    }
}

// app/Models/Promotion.php
class Promotion extends Model
{
    protected $fillable = [
        'code', 'discount_percentage', 'applies_to_discounted_price', 
        'starts_at', 'expires_at'
    ];

    protected $casts = [
        'discount_percentage' => 'decimal:2',
        'applies_to_discounted_price' => 'boolean',
        'starts_at' => 'datetime',
        'expires_at' => 'datetime',
    ];

    public function scopeActive(Builder $query): void
    {
        $now = now();
        $query->where('starts_at', '<=', $now)
              ->where('expires_at', '>=', $now);
    }

    public function scopeByCode(Builder $query, string $code): void
    {
        $query->where('code', $code);
    }
}

// app/Enums/CustomerTier.php
enum CustomerTier: string
{
    case BRONZE = 'bronze';
    case SILVER = 'silver';
    case GOLD = 'gold';
    case PLATINUM = 'platinum';
}

// app/Services/TaxService.php
class TaxService
{
    public const DEFAULT_TAX_RATE = 0.08;

    public function calculateTax(float $amount, bool $taxable = true): float
    {
        if (!$taxable) {
            return 0;
        }

        return round($amount * self::DEFAULT_TAX_RATE, 2);
    }
}
```