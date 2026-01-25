# Existing Codebase

## Schema

```php
Schema::create('subscriptions', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->string('status'); // active, cancelled, expired
    $table->timestamp('current_period_end');
    $table->boolean('reminder_7d_sent')->default(false);
    $table->boolean('reminder_1d_sent')->default(false);
    $table->timestamps();
});

Schema::create('users', function (Blueprint $table) {
    $table->id();
    $table->string('email');
    $table->string('timezone')->default('UTC');
    $table->timestamps();
});
```
