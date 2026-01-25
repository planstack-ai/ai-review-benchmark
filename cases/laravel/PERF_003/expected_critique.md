# Expected Critique

## Performance Bug: Queries Defeat Index Usage

### Location 1: `search()`
```php
->where('name', 'LIKE', "%{$query}%")
->orWhere('email', 'LIKE', "%{$query}%")
```

Leading wildcard (`%query`) prevents index usage. Database must scan every row.

### Location 2: `findByEmail()`
```php
->whereRaw('LOWER(email) = ?', [strtolower($email)])
```

Applying `LOWER()` function to column prevents using the unique index on email.

### Impact
1. **Full table scans**: Every query scans entire users table
2. **Slow searches**: Search times grow linearly with user count
3. **Database load**: High CPU usage for query processing
4. **Poor scalability**: Unusable at scale (100k+ users)

### Correct Implementations

For search:
```php
// Use full-text search (requires FULLTEXT index)
User::whereRaw('MATCH(name, email) AGAINST(? IN BOOLEAN MODE)', [$query])

// Or for prefix matching (uses index)
User::where('name', 'LIKE', "{$query}%")
    ->orWhere('email', 'LIKE', "{$query}%")
```

For email lookup:
```php
// Store emails lowercase in database, compare directly
User::where('email', strtolower($email))->first()

// Or add functional index on LOWER(email) if DB supports it
```

For status filtering:
```php
// Add index: $table->index('status')
// Select only needed columns
User::select(['id', 'name', 'email'])->where('status', $status)->get()
```

### Severity: High
Causes severe performance degradation as data grows.
