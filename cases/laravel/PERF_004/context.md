# Existing Codebase

## Schema

```php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->string('status');
    $table->decimal('total', 10, 2);
    $table->timestamps();
});

Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->decimal('price', 10, 2);
    $table->integer('stock');
    $table->timestamps();
});
```
