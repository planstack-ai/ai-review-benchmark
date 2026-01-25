# Existing Codebase

## Schema

```php
Schema::create('events', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->string('title');
    $table->timestamp('start_time');
    $table->timestamp('end_time');
    $table->string('timezone');
    $table->boolean('is_recurring')->default(false);
    $table->string('recurrence_pattern')->nullable(); // weekly
    $table->date('recurrence_end')->nullable();
    $table->timestamps();
});

Schema::create('event_occurrences', function (Blueprint $table) {
    $table->id();
    $table->foreignId('event_id')->constrained();
    $table->timestamp('start_time');
    $table->timestamp('end_time');
    $table->timestamps();
});
```
