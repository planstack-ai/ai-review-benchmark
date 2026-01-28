
# Django Test Cases Expansion Plan

## Overview

Expand Django test cases from 30 to 89 cases, matching Rails coverage.

## Current State

| Category | Django | Rails | Gap |
|----------|--------|-------|-----|
| CALC | 10 | 10 | 0 |
| AUTH | 7 | 7 | 0 |
| DJANGO | 8 | - | - |
| STOCK | 0 | 8 | **-8** |
| STATE | 0 | 7 | **-7** |
| TIME | 0 | 8 | **-8** |
| NOTIFY | 0 | 6 | **-6** |
| EXT | 0 | 6 | **-6** |
| PERF | 0 | 6 | **-6** |
| DATA | 0 | 6 | **-6** |
| FP | 5 | 20 | **-15** |
| **Total** | **30** | **84+11** | **-62** |

## Implementation Plan

### Phase 1: STOCK (Inventory) - 8 cases

Port Rails STOCK_001-008 to Django:

| ID | Name | Django Implementation |
|----|------|----------------------|
| STOCK_001 | stock_allocation_timing | Reserve at checkout with `F()` expressions |
| STOCK_002 | non_atomic_stock_update | `Product.objects.filter(stock__gt=0).update(stock=F('stock')-1)` |
| STOCK_003 | cart_stock_divergence | Validate stock in `checkout()` view |
| STOCK_004 | reserved_actual_confusion | `available = F('total_stock') - F('reserved_stock')` |
| STOCK_005 | zero_quantity_order | `MinValueValidator(1)` on quantity field |
| STOCK_006 | negative_stock_allowed | `Max(F('stock') + qty, Value(0))` |
| STOCK_007 | duplicate_stock_restoration | Idempotency check with `already_restored` flag |
| STOCK_008 | bundle_stock_calculation | `Min()` aggregate for component stocks |

### Phase 2: STATE (State Transitions) - 7 cases

Port Rails STATE_001-007 to Django:

| ID | Name | Django Implementation |
|----|------|----------------------|
| STATE_001 | invalid_state_transition | `django-fsm` or custom validator |
| STATE_002 | cancel_window_missing | Check `is_shipped` before `cancel()` |
| STATE_003 | payment_timeout | Check `expired_at` before `process_payment()` |
| STATE_004 | duplicate_payment | `select_for_update()` with `is_paid` check |
| STATE_005 | partial_cancel_integrity | Recalculate total after partial cancel |
| STATE_006 | refund_status_missing | Update `payment_status` after refund |
| STATE_007 | delivery_status_regression | Validate status progression |

### Phase 3: TIME - 8 cases

Port Rails TIME_001-008 to Django:

| ID | Name | Django Implementation |
|----|------|----------------------|
| TIME_001 | timezone_not_considered | `localtime()` / `timezone.activate()` |
| TIME_002 | sale_period_boundary | `datetime.combine(date, time.min)` |
| TIME_003 | coupon_expiry_comparison | `timezone.now() <= expires_at` (end of day) |
| TIME_004 | date_only_comparison | `.date()` extraction |
| TIME_005 | month_end_processing | `dateutil.relativedelta` |
| TIME_006 | year_crossing | `timedelta(days=1)` |
| TIME_007 | business_day_calculation | `numpy.busday_count` or `workalendar` |
| TIME_008 | past_delivery_date | Custom validator `validate_future_date` |

### Phase 4: NOTIFY (Notifications) - 6 cases

Port Rails NOTIFY_001-006 to Django:

| ID | Name | Django Implementation |
|----|------|----------------------|
| NOTIFY_001 | duplicate_email | `email_sent` flag check |
| NOTIFY_002 | async_error_swallowed | Celery `on_failure` handler |
| NOTIFY_003 | notification_timing | `post_save` signal with `payment_confirmed` |
| NOTIFY_004 | template_variable_nil | `{{ user.name\|default:"Valued Customer" }}` |
| NOTIFY_005 | recipient_mixup | Use `order.user` explicitly |
| NOTIFY_006 | bulk_rate_limit | Celery `rate_limit` or chunks |

### Phase 5: EXT (External Integration) - 6 cases

Port Rails EXT_001-006 to Django:

| ID | Name | Django Implementation |
|----|------|----------------------|
| EXT_001 | payment_timeout_unhandled | `requests.exceptions.Timeout` handling |
| EXT_002 | webhook_not_idempotent | `WebhookLog.objects.get_or_create(event_id=...)` |
| EXT_003 | api_call_in_transaction | Call API outside `transaction.atomic()` |
| EXT_004 | retry_duplicate_order | `get_or_create(idempotency_key=...)` |
| EXT_005 | inventory_sync_delay | `available = local_stock - pending_sync` |
| EXT_006 | shipping_error_swallowed | Check `response.status_code` |

### Phase 6: PERF (Performance) - 6 cases

Port Rails PERF_001-006 to Django:

| ID | Name | Django Implementation |
|----|------|----------------------|
| PERF_001 | n_plus_one_query | `select_related()` / `prefetch_related()` |
| PERF_002 | full_table_load | `iterator()` / `Paginator` |
| PERF_003 | unnecessary_eager_loading | Remove unused `select_related()` |
| PERF_004 | inefficient_count | `.count()` vs `len()` |
| PERF_005 | index_not_used | `db_index=True` on model field |
| PERF_006 | cache_key_design | `cache.get(f'orders_{user.id}')` |

### Phase 7: DATA (Data Integrity) - 6 cases

Port Rails DATA_001-006 to Django:

| ID | Name | Django Implementation |
|----|------|----------------------|
| DATA_001 | no_foreign_key | `ForeignKey` with `on_delete` |
| DATA_002 | unique_constraint_missing | `unique=True` + migration |
| DATA_003 | optimistic_lock_missing | Custom `version` field + check |
| DATA_004 | soft_delete_in_query | Custom manager with `deleted_at__isnull=True` |
| DATA_005 | master_data_history | Snapshot fields in OrderItem |
| DATA_006 | column_default_null | `default=0, null=False` |

### Phase 8: FP (False Positives) - 15 cases

Port Rails FP_006-020 to Django:

| ID | Name | Description |
|----|------|-------------|
| FP_006 | complex_nested_transaction | `transaction.atomic()` with `savepoint=True` |
| FP_007 | complex_callback_chain | Multiple signals in correct order |
| FP_008 | complex_state_machine | Complete FSM implementation |
| FP_009 | complex_calculation | Multi-step price calculation |
| FP_010 | complex_authorization | Role-based access with `PermissionRequiredMixin` |
| FP_011 | intentional_no_validation | Admin bypass for testing |
| FP_012 | intentional_raw_sql | Parameterized `cursor.execute()` |
| FP_013 | intentional_update_all | `bulk_update()` for performance |
| FP_014 | intentional_no_index | Low cardinality column |
| FP_015 | intentional_eager_load | Extra `prefetch_related()` for downstream |
| FP_016 | optimized_counter_cache | Denormalized count field |
| FP_017 | optimized_batch_insert | `bulk_create()` with `ignore_conflicts` |
| FP_018 | optimized_cache_warming | Intentional full load into cache |
| FP_019 | optimized_denormalization | Materialized view pattern |
| FP_020 | optimized_async_write | Celery with eventual consistency |

## File Structure

For each case:
```
cases/django/{CASE_ID}/
├── plan.md        # Specification (from plan field)
├── context.md     # Django models and existing code
├── impl.py        # Buggy implementation
└── meta.json      # Ground truth
```

## Implementation Order

1. **STOCK** (8 cases) - E-commerce core
2. **STATE** (7 cases) - Order workflow
3. **TIME** (8 cases) - Common Django issues
4. **NOTIFY** (6 cases) - Celery integration
5. **EXT** (6 cases) - API patterns
6. **PERF** (6 cases) - Django ORM optimization
7. **DATA** (6 cases) - Model constraints
8. **FP** (15 cases) - Complex correct implementations

## Deliverables

1. Update `patterns_django.yaml` with 62 new patterns
2. Generate 62 new test cases using `scripts/generator.py`
3. Manually review each case for Django idioms
4. Run benchmark to validate

## Expected Result

- Django: 30 -> 89 cases (+197%)
- Category coverage: 5 -> 12 categories
- Rails parity: 90%+

## Notes

- All patterns must use Django idioms (not direct Rails translations)
- Use `Decimal` instead of `float` for currency
- Use `django.utils.timezone` for time handling
- Use signals instead of callbacks
- Use `F()` expressions for atomic updates
