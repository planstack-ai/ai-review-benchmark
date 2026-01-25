# Existing Codebase

## Schema

```php
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('type'); // simple, bundle
    $table->integer('stock_quantity');
    $table->integer('reserved_quantity')->default(0);
    $table->decimal('price', 10, 2);
    $table->timestamps();
});

Schema::create('bundle_components', function (Blueprint $table) {
    $table->id();
    $table->foreignId('bundle_id')->constrained('products');
    $table->foreignId('component_id')->constrained('products');
    $table->integer('quantity'); // how many of this component per bundle
    $table->timestamps();
});

Schema::create('order_items', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained();
    $table->foreignId('product_id')->constrained();
    $table->integer('quantity');
    $table->timestamps();
});
```

## Models

```php
class Product extends Model
{
    public function bundleComponents()
    {
        return $this->hasMany(BundleComponent::class, 'bundle_id');
    }

    public function isBundle(): bool
    {
        return $this->type === 'bundle';
    }

    public function availableStock(): int
    {
        return $this->stock_quantity - $this->reserved_quantity;
    }
}
```
