# Existing Codebase

## Schema

```php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->decimal('subtotal', 10, 2);
    $table->decimal('tax_amount', 10, 2);
    $table->decimal('total', 10, 2);
    $table->string('status')->default('pending');
    $table->timestamps();
});

Schema::create('order_items', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained()->onDelete('cascade');
    $table->foreignId('product_id')->constrained();
    $table->integer('quantity');
    $table->decimal('unit_price', 10, 2);
    $table->timestamps();
});
```
