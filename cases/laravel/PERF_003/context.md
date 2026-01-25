# Existing Codebase

## Schema

```php
Schema::create('users', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('email')->unique();
    $table->string('status');
    $table->timestamps();
});

// Indexes
// - email: unique index
// - created_at: index
```
