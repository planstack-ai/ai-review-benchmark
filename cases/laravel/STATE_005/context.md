# Existing Codebase

## Schema

```php
Schema::create('tickets', function (Blueprint $table) {
    $table->id();
    $table->foreignId('customer_id')->constrained('users');
    $table->foreignId('assigned_agent_id')->nullable()->constrained('users');
    $table->string('subject');
    $table->text('description');
    $table->string('status'); // open, in_progress, waiting_customer, resolved, escalated, reopened, closed
    $table->string('priority')->default('normal');
    $table->timestamp('resolved_at')->nullable();
    $table->timestamps();
});

Schema::create('ticket_replies', function (Blueprint $table) {
    $table->id();
    $table->foreignId('ticket_id')->constrained();
    $table->foreignId('user_id')->constrained();
    $table->text('message');
    $table->boolean('is_internal')->default(false);
    $table->timestamps();
});
```
