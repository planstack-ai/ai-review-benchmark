# Expected Critique

## Critical Bug: Publishing Bypasses Approval

### Location
`publish()` method:
```php
if (!in_array($article->status, ['approved', 'unpublished', 'pending_review'])) {
```

### Problem
The `publish()` method allows publishing articles that are in `pending_review` status, completely bypassing the review and approval workflow.

According to valid transitions:
- `pending_review → approved` (must be reviewed first)
- `approved → published` (only approved articles can be published)

But the code allows:
- `pending_review → published` (INVALID - skips approval)

### Impact
1. **Quality control bypass**: Unreviewed content goes live
2. **Workflow violation**: Review process becomes meaningless
3. **Content risk**: Inappropriate or incorrect content published without oversight
4. **Compliance issues**: Required approval workflow not enforced

### Correct Implementation
```php
if (!in_array($article->status, ['approved', 'unpublished'])) {
    return [
        'success' => false,
        'message' => 'Article cannot be published in current state',
    ];
}
```

Or more explicitly:
```php
$publishableStates = ['approved', 'unpublished'];
if (!in_array($article->status, $publishableStates)) {
    return [
        'success' => false,
        'message' => 'Only approved or unpublished articles can be published',
    ];
}
```

### Severity: High
Completely bypasses the mandatory review workflow.
