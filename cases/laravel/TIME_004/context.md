# Existing Codebase

## Schema

```php
Schema::create('subscriptions', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->foreignId('plan_id')->constrained();
    $table->integer('billing_day'); // Day of month to bill (1-31)
    $table->timestamp('current_period_start');
    $table->timestamp('current_period_end');
    $table->timestamps();
});

Schema::create('plans', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->decimal('monthly_price', 8, 2);
    $table->timestamps();
});
```
