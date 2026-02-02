# Plan: Add Missing Laravel Test Patterns

## Overview

Laravel currently has 60 test cases, but is missing several key categories that other frameworks have:

| Category | Rails | Laravel | Django | Spring Boot Java |
|----------|-------|---------|--------|------------------|
| DATA | 7 | **0** | 6 | 7 |
| EXT | 7 | **0** | 6 | 7 |
| Framework-specific | 16 (RAILS) | **0** | 8 (DJANGO) | 8 (SPRING) |

**Goal**: Add ~30 new patterns to bring Laravel to ~90 cases (comparable to Rails/Django)

---

## Phase 1: DATA Patterns (Data Integrity) - 7 cases

Data integrity patterns focusing on database constraints, transactions, and data consistency.

| ID | Name | Description | Severity |
|----|------|-------------|----------|
| DATA_001 | no_foreign_key | Missing FK constraint allows orphan records | high |
| DATA_002 | unique_constraint_missing | Unique index missing - duplicate records allowed | critical |
| DATA_003 | optimistic_lock_missing | No lock_version - concurrent updates cause data loss | high |
| DATA_004 | soft_delete_in_query | Deleted records appear in queries (no global scope) | high |
| DATA_005 | master_data_history | Product changes affect historical order display | medium |
| DATA_006 | column_default_null | New nullable column causes downstream errors | medium |
| DATA_007 | cascade_delete_missing | Child records orphaned on parent delete | high |

### Laravel-specific implementation notes:
- Use Eloquent relationships and migrations
- Global scopes for soft deletes
- `$table->foreignId()->constrained()` for FK constraints

---

## Phase 2: EXT Patterns (External Integration) - 7 cases

External service integration patterns focusing on APIs, webhooks, and timeouts.

| ID | Name | Description | Severity |
|----|------|-------------|----------|
| EXT_001 | payment_timeout_unhandled | Payment gateway timeout leaves order in unknown state | critical |
| EXT_002 | webhook_not_idempotent | Same webhook processed multiple times | critical |
| EXT_003 | api_call_in_transaction | External API called inside DB transaction | critical |
| EXT_004 | retry_duplicate_order | Network retry creates duplicate orders | critical |
| EXT_005 | inventory_sync_delay | External warehouse sync delay not considered | high |
| EXT_006 | shipping_error_swallowed | Shipping API error silently ignored | high |
| EXT_007 | api_response_not_validated | External API response not validated/sanitized | high |

### Laravel-specific implementation notes:
- Use Laravel HTTP client with timeout handling
- `DB::afterCommit()` for external calls
- Webhook signature verification with Laravel's features

---

## Phase 3: LARAVEL Patterns (Framework-specific) - 16 cases

Laravel-specific anti-patterns and common mistakes.

| ID | Name | Description | Severity |
|----|------|-------------|----------|
| LARAVEL_001 | scope_not_used | Reimplementing where clause instead of using scope | medium |
| LARAVEL_002 | accessor_mutator_confusion | Accessor/mutator naming causes infinite loop | high |
| LARAVEL_003 | event_listener_order | Event listener execution order dependency | high |
| LARAVEL_004 | middleware_order_wrong | Middleware registered in wrong order | critical |
| LARAVEL_005 | job_outside_after_commit | Job dispatched before transaction commits | critical |
| LARAVEL_006 | mass_assignment_unguarded | Unguarded mass assignment vulnerability | critical |
| LARAVEL_007 | facade_mock_not_reset | Facade mock leaks between tests | medium |
| LARAVEL_008 | service_container_binding | Wrong binding type (singleton vs bind) | high |
| LARAVEL_009 | config_not_cached | Config called in loop (should be cached) | medium |
| LARAVEL_010 | route_model_binding_wrong | Implicit binding uses wrong key | high |
| LARAVEL_011 | policy_not_registered | Policy not auto-discovered, auth always fails | critical |
| LARAVEL_012 | observer_transaction | Observer fires outside transaction context | high |
| LARAVEL_013 | queue_connection_sync | Sync queue driver in production blocks requests | high |
| LARAVEL_014 | eloquent_boot_static | Static boot method called multiple times | high |
| LARAVEL_015 | collection_method_chain | Collection method returns new instance (not mutated) | medium |
| LARAVEL_016 | carbon_mutable_bug | Carbon mutability causes unexpected date changes | high |

### Implementation notes:
- Reference Django/Rails framework-specific patterns for style
- Focus on common Laravel-specific pitfalls
- Include Eloquent, Facades, Service Container, Queues, Events

---

## Implementation Steps

### Step 1: Update patterns_laravel.yaml
Add pattern definitions for all 30 new patterns:
- DATA_001 - DATA_007 (7 patterns)
- EXT_001 - EXT_007 (7 patterns)
- LARAVEL_001 - LARAVEL_016 (16 patterns)

### Step 2: Generate Test Cases
Use the generator script for each pattern:
```bash
python scripts/generator.py --framework laravel --pattern DATA_001
python scripts/generator.py --framework laravel --pattern DATA_002
# ... etc
```

### Step 3: Review Generated Cases
- Verify impl.php contains correct buggy code
- Verify meta.json has correct bug_anchor
- Ensure context.md provides sufficient context

### Step 4: Update Documentation
- Update CLAUDE.md with new Laravel case counts
- Update README if exists

---

## Expected Outcome

| Metric | Before | After |
|--------|--------|-------|
| Total Laravel cases | 60 | ~90 |
| DATA cases | 0 | 7 |
| EXT cases | 0 | 7 |
| LARAVEL cases | 0 | 16 |

This will bring Laravel test coverage to parity with Rails and Django.

---

## Priority Order

1. **High Priority**: LARAVEL patterns (framework-specific knowledge is unique value)
2. **Medium Priority**: EXT patterns (common integration bugs)
3. **Lower Priority**: DATA patterns (can leverage existing Rails patterns)

---

## Estimated Effort

- Pattern definition in YAML: ~2 hours
- Test case generation: ~4 hours (automated with review)
- Manual review and fixes: ~2 hours
- Total: ~8 hours
