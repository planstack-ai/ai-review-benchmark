# Existing Codebase

## Schema

```php
Schema::create('webhook_events', function (Blueprint $table) {
    $table->id();
    $table->string('event_id')->unique();
    $table->string('event_type');
    $table->json('payload');
    $table->string('status'); // pending, processed, failed
    $table->timestamps();
});

Schema::create('payments', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained();
    $table->string('external_id')->unique();
    $table->string('status');
    $table->decimal('amount', 10, 2);
    $table->timestamps();
});
```

## Config

```php
// config/payment.php
return [
    'webhook_secret' => env('PAYMENT_WEBHOOK_SECRET'),
];
```
