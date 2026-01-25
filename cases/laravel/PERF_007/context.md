# Existing Codebase

## Schema

```php
Schema::create('carts', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->timestamps();
});

Schema::create('cart_items', function (Blueprint $table) {
    $table->id();
    $table->foreignId('cart_id')->constrained();
    $table->foreignId('product_id')->constrained();
    $table->integer('quantity');
    $table->timestamps();
});

Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->decimal('price', 10, 2);
    $table->foreignId('category_id')->constrained();
    $table->timestamps();
});
```
