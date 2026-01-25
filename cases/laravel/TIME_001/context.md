# Existing Codebase

## Schema

```php
Schema::create('flash_sales', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->timestamp('starts_at');
    $table->timestamp('ends_at');
    $table->boolean('active')->default(true);
    $table->timestamps();
});

Schema::create('flash_sale_items', function (Blueprint $table) {
    $table->id();
    $table->foreignId('flash_sale_id')->constrained();
    $table->foreignId('product_id')->constrained();
    $table->decimal('sale_price', 10, 2);
    $table->integer('quantity_limit')->nullable();
    $table->integer('sold_count')->default(0);
    $table->timestamps();
});
```

## Config

```php
// config/app.php
'timezone' => 'UTC',
```
