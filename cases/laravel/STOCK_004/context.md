# Existing Codebase

## Schema

```php
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('sku')->unique();
    $table->integer('stock_quantity');
    $table->timestamps();
});

Schema::create('inventory_adjustments', function (Blueprint $table) {
    $table->id();
    $table->foreignId('product_id')->constrained();
    $table->foreignId('user_id')->constrained();
    $table->integer('quantity_change'); // positive or negative
    $table->integer('stock_before');
    $table->integer('stock_after');
    $table->string('reason_code'); // damaged, audit, correction, shrinkage
    $table->text('notes')->nullable();
    $table->string('status'); // pending, approved, completed
    $table->timestamps();
});
```

## Reason Codes

- `damaged`: Products damaged in warehouse
- `audit`: Adjustment from physical count
- `correction`: Error correction
- `shrinkage`: Missing inventory
