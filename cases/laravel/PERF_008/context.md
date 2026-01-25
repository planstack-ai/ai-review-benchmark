# Existing Codebase

## Schema

```php
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->decimal('price', 10, 2);
    $table->boolean('active')->default(true);
    $table->timestamps();
});

Schema::create('price_histories', function (Blueprint $table) {
    $table->id();
    $table->foreignId('product_id')->constrained();
    $table->decimal('old_price', 10, 2);
    $table->decimal('new_price', 10, 2);
    $table->timestamps();
});
```
