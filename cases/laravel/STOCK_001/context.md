# Existing Codebase

## Schema

```php
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->decimal('price', 10, 2);
    $table->integer('stock_quantity')->default(0);
    $table->integer('reserved_quantity')->default(0);
    $table->boolean('available')->default(true);
    $table->timestamps();
});

Schema::create('carts', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->decimal('total_amount', 10, 2)->default(0);
    $table->timestamps();
});

Schema::create('cart_items', function (Blueprint $table) {
    $table->id();
    $table->foreignId('cart_id')->constrained();
    $table->foreignId('product_id')->constrained();
    $table->integer('quantity');
    $table->decimal('unit_price', 10, 2);
    $table->timestamps();
});

Schema::create('stock_reservations', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->foreignId('product_id')->constrained();
    $table->integer('quantity');
    $table->timestamp('expires_at');
    $table->timestamps();
});
```

## Business Rules

**Stock Reservation Timing**:
- Stock should NOT be reserved when adding to cart (causes stock lockup)
- Stock should be reserved only at checkout/payment
- This prevents abandoned carts from blocking inventory
