# Existing Codebase

## Config

```php
// config/ratelimit.php
return [
    'default' => [
        'max_requests' => 60,
        'window_seconds' => 60,
    ],
    'api' => [
        'max_requests' => 100,
        'window_seconds' => 60,
    ],
];
```
