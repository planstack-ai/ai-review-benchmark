# Existing Codebase

## Schema

```php
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->integer('stock_quantity')->default(0);
    $table->integer('expected_quantity')->default(0); // incoming stock
    $table->integer('preorder_count')->default(0);
    $table->boolean('preorder_enabled')->default(false);
    $table->timestamp('expected_arrival_date')->nullable();
    $table->timestamps();
});

Schema::create('preorders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->foreignId('product_id')->constrained();
    $table->integer('quantity');
    $table->string('status'); // pending, converted, cancelled
    $table->timestamps();
});

Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->foreignId('preorder_id')->nullable()->constrained();
    $table->string('status');
    $table->timestamps();
});
```
