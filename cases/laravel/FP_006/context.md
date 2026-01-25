# Existing Codebase

## Schema

```php
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->integer('stock_quantity');
    $table->timestamps();
});

Schema::create('inventory_logs', function (Blueprint $table) {
    $table->id();
    $table->foreignId('product_id')->constrained();
    $table->integer('quantity_change');
    $table->integer('stock_before');
    $table->integer('stock_after');
    $table->string('reason');
    $table->timestamps();
});
```
