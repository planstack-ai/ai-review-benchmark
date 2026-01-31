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
            $table->decimal('price_cents', 10, 0);
            $table->decimal('cost_cents', 10, 0)->nullable();
            $table->string('currency', 3)->default('USD');
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('products');
    }
};
```

## Models

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Builder;

class Product extends Model
{
    use HasFactory;

    protected $fillable = [
        'name',
        'sku',
        'price_cents',
        'cost_cents',
        'currency',
        'is_active',
    ];

    protected $casts = [
        'price_cents' => 'integer',
        'cost_cents' => 'integer',
        'is_active' => 'boolean',
    ];

    public function scopeActive(Builder $query): void
    {
        $query->where('is_active', true);
    }

    public function scopeInCurrency(Builder $query, string $currency): void
    {
        $query->where('currency', $currency);
    }

    public function getPriceDollarsAttribute(): float
    {
        return $this->price_cents / 100;
    }

    public function setPriceDollarsAttribute(float $value): void
    {
        $this->price_cents = (int) round($value * 100);
    }

    public function getCostDollarsAttribute(): ?float
    {
        return $this->cost_cents ? $this->cost_cents / 100 : null;
    }

    public function setCostDollarsAttribute(?float $value): void
    {
        $this->cost_cents = $value ? (int) round($value * 100) : null;
    }

    public function getMarginAttribute(): ?float
    {
        if (!$this->cost_cents || $this->price_cents <= 0) {
            return null;
        }

        return (($this->price_cents - $this->cost_cents) / $this->price_cents) * 100;
    }
}
```

```php
<?php

namespace App\Services;

class CurrencyFormatter
{
    public static function format(int $cents, string $currency = 'USD'): string
    {
        $amount = $cents / 100;
        
        return match ($currency) {
            'USD' => '$' . number_format($amount, 2),
            'EUR' => '€' . number_format($amount, 2, ',', '.'),
            'GBP' => '£' . number_format($amount, 2),
            default => $currency . ' ' . number_format($amount, 2),
        };
    }

    public static function formatWithoutSymbol(int $cents): string
    {
        return number_format($cents / 100, 2);
    }
}
```