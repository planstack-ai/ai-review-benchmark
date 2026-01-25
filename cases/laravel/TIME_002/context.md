# Existing Codebase

## Schema

```php
Schema::create('coupons', function (Blueprint $table) {
    $table->id();
    $table->string('code')->unique();
    $table->decimal('discount_amount', 10, 2)->nullable();
    $table->integer('discount_percent')->nullable();
    $table->date('valid_from');
    $table->date('valid_until');
    $table->integer('usage_limit')->nullable();
    $table->integer('used_count')->default(0);
    $table->boolean('active')->default(true);
    $table->timestamps();
});
```
