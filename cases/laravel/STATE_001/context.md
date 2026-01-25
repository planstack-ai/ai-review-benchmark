# Existing Codebase

## Schema

```php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->string('status')->default('pending');
    $table->decimal('total', 10, 2);
    $table->timestamps();
});

Schema::create('order_status_histories', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained();
    $table->string('from_status');
    $table->string('to_status');
    $table->foreignId('changed_by')->nullable()->constrained('users');
    $table->text('notes')->nullable();
    $table->timestamps();
});
```

## Constants

```php
class OrderStatus
{
    public const PENDING = 'pending';
    public const PAID = 'paid';
    public const PROCESSING = 'processing';
    public const SHIPPED = 'shipped';
    public const DELIVERED = 'delivered';
    public const CANCELLED = 'cancelled';
    public const REFUNDED = 'refunded';
}
```
