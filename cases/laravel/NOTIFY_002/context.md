# Existing Codebase

## Schema

```php
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->integer('stock_quantity');
    $table->integer('reorder_point');
    $table->timestamp('last_low_stock_alert_at')->nullable();
    $table->timestamps();
});

Schema::create('users', function (Blueprint $table) {
    $table->id();
    $table->string('email');
    $table->string('role'); // admin, inventory_manager, staff
    $table->timestamps();
});
```
