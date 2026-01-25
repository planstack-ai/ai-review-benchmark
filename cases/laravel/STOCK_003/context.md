# Existing Codebase

## Schema

```php
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->integer('stock_quantity');
    $table->integer('reserved_quantity')->default(0);
    $table->timestamps();
});

Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->string('status'); // pending, paid, shipped, delivered, cancelled
    $table->timestamp('delivered_at')->nullable();
    $table->timestamps();
});

Schema::create('order_items', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained();
    $table->foreignId('product_id')->constrained();
    $table->integer('quantity');
    $table->boolean('returned')->default(false);
    $table->timestamps();
});

Schema::create('returns', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained();
    $table->foreignId('order_item_id')->constrained();
    $table->integer('quantity');
    $table->string('status'); // pending, approved, completed
    $table->timestamps();
});
```

## Models

```php
class Product extends Model
{
    public function availableStock(): int
    {
        return $this->stock_quantity - $this->reserved_quantity;
    }
}
```
