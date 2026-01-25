# Existing Codebase

## Schema

```php
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('sku')->unique();
    $table->integer('stock_quantity');
    $table->integer('reserved_quantity')->default(0);
    $table->integer('reorder_point');
    $table->integer('safety_stock');
    $table->decimal('daily_demand', 8, 2);
    $table->integer('lead_time_days');
    $table->timestamps();
});

Schema::create('purchase_orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('product_id')->constrained();
    $table->foreignId('supplier_id')->constrained();
    $table->integer('quantity');
    $table->string('status'); // pending, confirmed, shipped, received, cancelled
    $table->timestamp('expected_date')->nullable();
    $table->timestamps();
});

Schema::create('suppliers', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->boolean('active')->default(true);
    $table->timestamps();
});
```

## Model

```php
class Product extends Model
{
    public function availableStock(): int
    {
        return $this->stock_quantity - $this->reserved_quantity;
    }

    public function primarySupplier()
    {
        return $this->belongsTo(Supplier::class, 'primary_supplier_id');
    }
}
```
