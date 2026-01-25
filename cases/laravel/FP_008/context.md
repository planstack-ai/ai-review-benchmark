# Existing Codebase

## Schema

```php
Schema::create('uploads', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->string('original_name');
    $table->string('stored_name');
    $table->string('mime_type');
    $table->integer('size');
    $table->string('disk')->default('local');
    $table->timestamps();
});
```

## Config

```php
// config/uploads.php
return [
    'max_size' => 10 * 1024 * 1024, // 10MB
    'allowed_mimes' => ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'],
];
```
