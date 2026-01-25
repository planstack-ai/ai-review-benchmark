# Existing Codebase

## Schema

```php
Schema::create('subscriptions', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->foreignId('plan_id')->constrained();
    $table->string('status'); // trial, active, paused, cancelled, expired
    $table->timestamp('trial_ends_at')->nullable();
    $table->timestamp('current_period_ends_at')->nullable();
    $table->timestamp('paused_at')->nullable();
    $table->timestamp('cancelled_at')->nullable();
    $table->timestamps();
});

Schema::create('plans', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->decimal('price', 8, 2);
    $table->integer('trial_days')->default(14);
    $table->timestamps();
});
```
