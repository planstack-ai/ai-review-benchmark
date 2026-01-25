# Expected Critique

## Security Bug: Password Reset Token Not Hashed

### Location
`sendResetLink()` method:
```php
DB::table('password_resets')->insert([
    'email' => $user->email,
    'token' => $token, // Plain text!
    'created_at' => now(),
]);
```

And `validateToken()`:
```php
$reset = DB::table('password_resets')
    ->where('token', $token) // Direct comparison
    ->first();
```

### Problem
The password reset token is stored in plain text in the database. If an attacker gains read access to the database (SQL injection, backup leak, insider threat), they can:
1. See all active reset tokens
2. Use any token to reset any user's password
3. Take over user accounts

### Security Best Practice
Reset tokens should be treated like passwords - hash before storing, compare hashes when validating.

### Impact
1. **Account takeover**: Attacker can reset any password with DB access
2. **Privilege escalation**: Can target admin accounts
3. **Compliance violation**: Fails security audit requirements
4. **Breach amplification**: DB leak becomes account compromise

### Correct Implementation
```php
public function sendResetLink(string $email): array
{
    // ...
    $token = Str::random(64);

    DB::table('password_resets')->insert([
        'email' => $user->email,
        'token' => Hash::make($token), // Store hash
        'created_at' => now(),
    ]);

    // Send plain token to user via email
    $user->notify(new PasswordResetNotification($token));
    // ...
}

public function validateToken(string $email, string $token): bool
{
    $reset = DB::table('password_resets')
        ->where('email', $email)
        ->first();

    if (!$reset) {
        return false;
    }

    // Compare using hash check
    if (!Hash::check($token, $reset->token)) {
        return false;
    }

    // Check expiry...
}
```

### Severity: High
Database breach would expose all active password reset tokens.
