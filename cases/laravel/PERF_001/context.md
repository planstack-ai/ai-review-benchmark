# Existing Codebase

## Schema

```php
Schema::create('categories', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('slug');
    $table->timestamps();
});

Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->foreignId('category_id')->constrained();
    $table->string('name');
    $table->decimal('price', 10, 2);
    $table->boolean('active')->default(true);
    $table->timestamps();
});
```
