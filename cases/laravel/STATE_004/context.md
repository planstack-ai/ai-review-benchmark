# Existing Codebase

## Schema

```php
Schema::create('articles', function (Blueprint $table) {
    $table->id();
    $table->foreignId('author_id')->constrained('users');
    $table->string('title');
    $table->text('content');
    $table->string('status'); // draft, pending_review, approved, published, unpublished, archived
    $table->timestamp('published_at')->nullable();
    $table->timestamps();
});

Schema::create('article_reviews', function (Blueprint $table) {
    $table->id();
    $table->foreignId('article_id')->constrained();
    $table->foreignId('reviewer_id')->constrained('users');
    $table->string('decision'); // approved, changes_requested
    $table->text('comments')->nullable();
    $table->timestamps();
});
```
