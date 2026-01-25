# Existing Codebase

## Schema

```php
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->integer('stock')->default(0);
    $table->timestamps();
});
```

## Atomic Update Pattern

To prevent race conditions, use atomic updates:

```php
// CORRECT: Atomic update
Product::where('id', $id)
    ->where('stock', '>=', $quantity)
    ->decrement('stock', $quantity);

// WRONG: Read-then-write race condition
$product = Product::find($id);
if ($product->stock >= $quantity) {
    $product->update(['stock' => $product->stock - $quantity]);
}
```
