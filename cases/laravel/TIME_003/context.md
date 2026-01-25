# Existing Codebase

## Schema

```php
Schema::create('time_slots', function (Blueprint $table) {
    $table->id();
    $table->date('date');
    $table->time('start_time');
    $table->time('end_time');
    $table->boolean('available')->default(true);
    $table->timestamps();
});

Schema::create('bookings', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->foreignId('time_slot_id')->constrained();
    $table->string('status'); // confirmed, cancelled
    $table->timestamps();
});
```

## Config

```php
// Business operates in Tokyo timezone
define('BUSINESS_TIMEZONE', 'Asia/Tokyo');
```
