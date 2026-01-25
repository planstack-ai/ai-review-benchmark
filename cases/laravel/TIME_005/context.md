# Existing Codebase

## Schema

```php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->decimal('total', 10, 2);
    $table->string('status');
    $table->timestamps(); // created_at stored in UTC
});

Schema::create('daily_reports', function (Blueprint $table) {
    $table->id();
    $table->date('report_date');
    $table->integer('order_count');
    $table->decimal('total_revenue', 12, 2);
    $table->decimal('average_order_value', 10, 2);
    $table->timestamps();
});
```

## Config

```php
define('BUSINESS_TIMEZONE', 'America/New_York');
```
