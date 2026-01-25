# Existing Codebase

## Schema

```php
Schema::create('warehouses', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('code')->unique();
    $table->timestamps();
});

Schema::create('warehouse_stock', function (Blueprint $table) {
    $table->id();
    $table->foreignId('warehouse_id')->constrained();
    $table->foreignId('product_id')->constrained();
    $table->integer('quantity');
    $table->integer('reserved_quantity')->default(0);
    $table->unique(['warehouse_id', 'product_id']);
    $table->timestamps();
});

Schema::create('stock_transfers', function (Blueprint $table) {
    $table->id();
    $table->foreignId('product_id')->constrained();
    $table->foreignId('source_warehouse_id')->constrained('warehouses');
    $table->foreignId('destination_warehouse_id')->constrained('warehouses');
    $table->integer('quantity');
    $table->string('status'); // pending, in_transit, completed, cancelled
    $table->timestamp('shipped_at')->nullable();
    $table->timestamp('received_at')->nullable();
    $table->timestamps();
});
```

## Model

```php
class WarehouseStock extends Model
{
    public function availableQuantity(): int
    {
        return $this->quantity - $this->reserved_quantity;
    }
}
```
