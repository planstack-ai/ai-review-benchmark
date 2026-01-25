# Existing Codebase

## Schema

```php
Schema::create('notifications', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->string('type');
    $table->string('channel');
    $table->json('data');
    $table->timestamp('sent_at')->nullable();
    $table->timestamps();
});
```
