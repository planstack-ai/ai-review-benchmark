# Existing Codebase

## Schema

```php
Schema::create('users', function (Blueprint $table) {
    $table->id();
    $table->string('email');
    $table->boolean('email_notifications')->default(true);
    $table->timestamps();
});

Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->string('status');
    $table->string('tracking_number')->nullable();
    $table->timestamps();
});
```

## Notification Classes

```php
class OrderShippedNotification extends Notification
{
    public function __construct(public Order $order) {}
}

class OrderDeliveredNotification extends Notification
{
    public function __construct(public Order $order) {}
}
```
