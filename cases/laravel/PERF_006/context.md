# Existing Codebase

## Schema

```php
Schema::create('users', function (Blueprint $table) {
    $table->id();
    $table->string('email');
    $table->boolean('email_notifications')->default(true);
    $table->timestamps();
});

Schema::create('notification_logs', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->string('type');
    $table->string('status');
    $table->timestamps();
});
```
