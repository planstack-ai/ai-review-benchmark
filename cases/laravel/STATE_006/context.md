# Existing Codebase

## Schema

```php
Schema::create('candidates', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('email')->unique();
    $table->foreignId('job_id')->constrained();
    $table->string('status'); // applied, phone_screen, technical, onsite, offer, accepted, declined, rejected
    $table->timestamps();
});

Schema::create('interviews', function (Blueprint $table) {
    $table->id();
    $table->foreignId('candidate_id')->constrained();
    $table->string('type'); // phone_screen, technical, onsite
    $table->foreignId('interviewer_id')->constrained('users');
    $table->timestamp('scheduled_at');
    $table->string('result')->nullable(); // passed, failed
    $table->text('feedback')->nullable();
    $table->timestamps();
});
```
