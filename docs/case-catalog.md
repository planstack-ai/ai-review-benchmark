# Test Case Catalog

*Generated: 2026-01-26 12:12:37*

This document provides a comprehensive reference for all test cases in the benchmark.

### Evaluation Mode

| Mode | Description |
|------|-------------|
| `severity` | Keyword & severity-based automatic evaluation |
| `semantic` | LLM-based semantic evaluation vs `expected_critique.md` |
| `dual` | Explicit + implicit context comparison (for Implicit Knowledge cases) |

## Summary

| Framework | Bug Cases | FP Cases | Total |
|-----------|-----------|----------|-------|
| Django | 25 | 5 | 30 |
| Laravel | 50 | 10 | 60 |
| Rails | 86 | 13 | 99 |
| **Total** | **161** | **28** | **189** |

> Counts are derived from case metadata and updated automatically by `scripts/generate_catalog.py`.

## Rails Cases

### Spec Alignment

Cases that test Plan vs Code alignment.

#### CALC - Price Calculation (11)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [CALC_001](../cases/rails/CALC_001/plan.md) | critical | easy | Discount rate direction wrong, becomes 90% off | calculation, discount, member | semantic |
| [CALC_002](../cases/rails/CALC_002/plan.md) | high | medium | Tax calculation order wrong - applying tax befo... | calculation, tax, discount | semantic |
| [CALC_003](../cases/rails/CALC_003/plan.md) | medium | medium | Inconsistent rounding - round per item then sum... | calculation, rounding | semantic |
| [CALC_004](../cases/rails/CALC_004/plan.md) | high | medium | Floating point precision error - 0.1 + 0.2 != 0... | calculation, currency, precision | semantic |
| [CALC_005](../cases/rails/CALC_005/plan.md) | high | easy | Hardcoded old tax rate - still using 8% instead... | calculation, tax, hardcode | semantic |
| [CALC_006](../cases/rails/CALC_006/plan.md) | medium | easy | Boundary condition error - >= 5000 vs > 5000 | calculation, shipping, boundary | semantic |
| [CALC_007](../cases/rails/CALC_007/plan.md) | medium | medium | Points calculated on pre-discount amount instea... | calculation, points, discount | semantic |
| [CALC_008](../cases/rails/CALC_008/plan.md) | high | medium | Coupon stacking allowed - multiple coupons can ... | calculation, coupon, validation | semantic |
| [CALC_009](../cases/rails/CALC_009/plan.md) | medium | medium | Minimum check on pre-discount amount instead of... | calculation, validation, minimum | semantic |
| [CALC_010](../cases/rails/CALC_010/plan.md) | critical | hard | Integer overflow on unit_price * quantity for l... | calculation, overflow, bulk | semantic |
| [CALC_011](../cases/rails/CALC_011/plan.md) | critical | medium | Calculation order differs from specification; c... | calculation, spec_violation, pricing | dual |

#### STOCK - Inventory & Quantity (8)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [STOCK_001](../cases/rails/STOCK_001/plan.md) | high | medium | Stock allocated at cart addition instead of pay... | inventory, timing, reservation | semantic |
| [STOCK_002](../cases/rails/STOCK_002/plan.md) | critical | hard | Race condition between stock check and update | inventory, race_condition, atomic | semantic |
| [STOCK_003](../cases/rails/STOCK_003/plan.md) | high | medium | Cart quantity not revalidated - stock may deple... | inventory, cart, validation | semantic |
| [STOCK_004](../cases/rails/STOCK_004/plan.md) | critical | medium | Reserved stock counted as available - double co... | inventory, reservation, counting | semantic |
| [STOCK_005](../cases/rails/STOCK_005/plan.md) | medium | easy | Zero quantity orders allowed through validation... | inventory, validation, quantity | semantic |
| [STOCK_006](../cases/rails/STOCK_006/plan.md) | high | medium | Cancellation processing can drive stock negative | inventory, cancellation, negative | semantic |
| [STOCK_007](../cases/rails/STOCK_007/plan.md) | critical | medium | Cancel spam increases stock - no idempotency check | inventory, cancellation, idempotency | semantic |
| [STOCK_008](../cases/rails/STOCK_008/plan.md) | high | hard | Bundle stock not calculated as minimum of compo... | inventory, bundle, calculation | semantic |

#### STATE - State Transitions (7)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [STATE_001](../cases/rails/STATE_001/plan.md) | critical | medium | Invalid transition allowed - shipped can go bac... | state, transition, validation | semantic |
| [STATE_002](../cases/rails/STATE_002/plan.md) | high | easy | Cancellation succeeds even after shipment | state, cancellation, validation | semantic |
| [STATE_003](../cases/rails/STATE_003/plan.md) | critical | medium | Payment accepted after order expiration time | state, payment, timeout | semantic |
| [STATE_004](../cases/rails/STATE_004/plan.md) | critical | hard | Double-click charges twice - no duplicate check | state, payment, duplicate | semantic |
| [STATE_005](../cases/rails/STATE_005/plan.md) | high | medium | Total amount wrong after partial item cancellation | state, cancellation, calculation | semantic |
| [STATE_006](../cases/rails/STATE_006/plan.md) | high | easy | Payment shows unpaid despite refund completion | state, refund, status | semantic |
| [STATE_007](../cases/rails/STATE_007/plan.md) | medium | medium | Delivered can regress to shipping status | state, delivery, regression | semantic |

#### AUTH - Authorization (7)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [AUTH_001](../cases/rails/AUTH_001/plan.md) | critical | easy | IDOR vulnerability - can access other user's or... | authorization, idor, security | semantic |
| [AUTH_002](../cases/rails/AUTH_002/plan.md) | critical | easy | Can manipulate other user's cart by specifying ... | authorization, cart, security | semantic |
| [AUTH_003](../cases/rails/AUTH_003/plan.md) | high | medium | Deleted user's order data still accessible | authorization, deleted, privacy | semantic |
| [AUTH_004](../cases/rails/AUTH_004/plan.md) | critical | easy | Regular users can change prices - admin check m... | authorization, admin, permission | semantic |
| [AUTH_005](../cases/rails/AUTH_005/plan.md) | high | medium | Guest users getting member pricing - membership... | authorization, membership, pricing | semantic |
| [AUTH_006](../cases/rails/AUTH_006/plan.md) | high | easy | Can access other user's points via API | authorization, points, api | semantic |
| [AUTH_007](../cases/rails/AUTH_007/plan.md) | high | medium | Can use another user's coupon code | authorization, coupon, ownership | semantic |

#### TIME - Time & Duration (8)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [TIME_001](../cases/rails/TIME_001/plan.md) | medium | medium | Timezone not considered - UTC saved, displayed ... | time, timezone, display | semantic |
| [TIME_002](../cases/rails/TIME_002/plan.md) | high | medium | Sale period boundary error - 0:00 start becomes... | time, boundary, sale | semantic |
| [TIME_003](../cases/rails/TIME_003/plan.md) | medium | easy | Off-by-one on expiry - using < instead of <= | time, expiry, comparison | semantic |
| [TIME_004](../cases/rails/TIME_004/plan.md) | medium | medium | Time truncation causes next-day treatment | time, date, comparison | semantic |
| [TIME_005](../cases/rails/TIME_005/plan.md) | high | hard | Invalid date error - February 30 doesn't exist | time, month_end, validation | semantic |
| [TIME_006](../cases/rails/TIME_006/plan.md) | high | hard | Year crossing logic error - 12/31 to 1/1 fails | time, year_end, boundary | semantic |
| [TIME_007](../cases/rails/TIME_007/plan.md) | medium | medium | Weekends and holidays not excluded from busines... | time, business_day, holiday | semantic |
| [TIME_008](../cases/rails/TIME_008/plan.md) | medium | easy | Past delivery dates accepted | time, validation, future | semantic |

#### NOTIFY - Notifications (6)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [NOTIFY_001](../cases/rails/NOTIFY_001/plan.md) | high | medium | Retry logic sends duplicate confirmation emails | notification, email, duplicate | semantic |
| [NOTIFY_002](../cases/rails/NOTIFY_002/plan.md) | high | medium | Background job fails silently - user not notified | notification, async, error | semantic |
| [NOTIFY_003](../cases/rails/NOTIFY_003/plan.md) | high | medium | Order complete email sent before payment confir... | notification, timing, order | semantic |
| [NOTIFY_004](../cases/rails/NOTIFY_004/plan.md) | medium | easy | Template variable user.name is nil causing error | notification, template, nil | semantic |
| [NOTIFY_005](../cases/rails/NOTIFY_005/plan.md) | critical | medium | Email sent to wrong user due to variable scope | notification, recipient, privacy | semantic |
| [NOTIFY_006](../cases/rails/NOTIFY_006/plan.md) | medium | medium | Mass email send gets blocked by rate limit | notification, bulk, rate_limit | semantic |

### Implicit Knowledge

Cases that test detection of issues not explicitly in Plan.

#### EXT - External Integration (7)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [EXT_001](../cases/rails/EXT_001/plan.md) | critical | hard | Payment timeout leaves order in unknown state | external, payment, timeout | dual |
| [EXT_002](../cases/rails/EXT_002/plan.md) | critical | medium | Same webhook processed multiple times | external, webhook, idempotency | dual |
| [EXT_003](../cases/rails/EXT_003/plan.md) | critical | hard | Payment charged even if transaction rolls back | external, transaction, api | dual |
| [EXT_004](../cases/rails/EXT_004/plan.md) | critical | hard | Network retry creates duplicate order records | external, retry, duplicate | dual |
| [EXT_005](../cases/rails/EXT_005/plan.md) | high | hard | External warehouse stock diff not considered | external, inventory, sync | dual |
| [EXT_006](../cases/rails/EXT_006/plan.md) | high | medium | Shipping API error swallowed, treated as success | external, shipping, error | dual |
| [EXT_007](../cases/rails/EXT_007/plan.md) | critical | hard | Multiple injection vulnerabilities: path traver... | security, injection, path_traversal | dual |

#### PERF - Performance (8)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [PERF_001](../cases/rails/PERF_001/plan.md) | high | easy | N+1 query on order items accessing product names | performance, n_plus_one, eager_load | dual |
| [PERF_002](../cases/rails/PERF_002/plan.md) | critical | easy | Loading all orders into memory - Order.all on 1... | performance, memory, batch | dual |
| [PERF_003](../cases/rails/PERF_003/plan.md) | medium | medium | Eager loading unused associations wastes resources | performance, eager_load, waste | dual |
| [PERF_004](../cases/rails/PERF_004/plan.md) | medium | easy | Loading all records just to count - items.lengt... | performance, count, query | dual |
| [PERF_005](../cases/rails/PERF_005/plan.md) | high | medium | Search condition on non-indexed column causes f... | performance, index, query | dual |
| [PERF_006](../cases/rails/PERF_006/plan.md) | high | medium | Same cache key for all users - cache collision | performance, cache, key | dual |
| [PERF_007](../cases/rails/PERF_007/plan.md) | high | medium | In-memory aggregation and sorting on potentiall... | performance, memory, aggregation | dual |
| [PERF_008](../cases/rails/PERF_008/plan.md) | high | hard | N+1 queries in bulk_update_metrics creates new ... | performance, n_plus_one, bulk | dual |

#### DATA - Data Integrity (7)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [DATA_001](../cases/rails/DATA_001/plan.md) | high | medium | No foreign key constraint - orphan records on p... | data, foreign_key, integrity | dual |
| [DATA_002](../cases/rails/DATA_002/plan.md) | critical | easy | Unique constraint missing - duplicate emails al... | data, unique, constraint | dual |
| [DATA_003](../cases/rails/DATA_003/plan.md) | high | medium | No optimistic locking - last write wins silently | data, locking, concurrent | dual |
| [DATA_004](../cases/rails/DATA_004/plan.md) | high | easy | Deleted records appear in search results | data, soft_delete, query | dual |
| [DATA_005](../cases/rails/DATA_005/plan.md) | medium | hard | Product name change affects past order display | data, history, snapshot | dual |
| [DATA_006](../cases/rails/DATA_006/plan.md) | medium | medium | New column defaults to NULL causing downstream ... | data, default, null | dual |
| [DATA_007](../cases/rails/DATA_007/plan.md) | high | hard | Batch import reports incorrect counts; insert_a... | data_integrity, batch, counting | dual |

#### RAILS - Rails-Specific (16)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [RAILS_001](../cases/rails/RAILS_001/plan.md) | medium | easy | Scope not used - reimplementing where(status: '... | rails, scope, dry | dual |
| [RAILS_002](../cases/rails/RAILS_002/plan.md) | medium | easy | String literal comparison instead of enum | rails, enum, type_safety | dual |
| [RAILS_003](../cases/rails/RAILS_003/plan.md) | high | hard | before_save callback order affects result | rails, callback, order | dual |
| [RAILS_004](../cases/rails/RAILS_004/plan.md) | high | easy | dependent: :destroy missing - children orphaned... | rails, association, dependent | dual |
| [RAILS_005](../cases/rails/RAILS_005/plan.md) | critical | medium | Job enqueued in transaction - runs even if roll... | rails, job, transaction | dual |
| [RAILS_006](../cases/rails/RAILS_006/plan.md) | critical | easy | Strong Parameters missing - mass assignment vul... | rails, security, strong_params | dual |
| [RAILS_007](../cases/rails/RAILS_007/plan.md) | high | hard | Race condition creates duplicate records | rails, race_condition, create | dual |
| [RAILS_008](../cases/rails/RAILS_008/plan.md) | high | medium | update_all skips callbacks and validations | rails, update_all, callback | dual |
| [RAILS_009](../cases/rails/RAILS_009/plan.md) | medium | easy | select loads full objects when only attributes ... | rails, pluck, performance | dual |
| [RAILS_010](../cases/rails/RAILS_010/plan.md) | medium | hard | Wrong eager loading method generates unexpected... | rails, eager_load, query | dual |
| [RAILS_011](../cases/rails/RAILS_011/plan.md) | critical | hard | Nested transaction without requires_new: true c... | rails, transaction, nesting | dual |
| [RAILS_012](../cases/rails/RAILS_012/plan.md) | critical | hard | External API call (PaymentGateway.charge) insid... | rails, transaction, external_api | severity |
| [RAILS_013](../cases/rails/RAILS_013/plan.md) | critical | hard | Balance transfer without pessimistic locking (l... | rails, transaction, pessimistic_lock | severity |
| [RAILS_014](../cases/rails/RAILS_014/plan.md) | high | medium | Using unscoped.featured does not fully remove d... | rails, default_scope, scope | severity |
| [RAILS_015](../cases/rails/RAILS_015/plan.md) | high | medium | Enum scopes (Order.pending) exclude rows where ... | rails, enum, null | severity |
| [RAILS_016](../cases/rails/RAILS_016/plan.md) | high | medium | Callbacks declared and manually executed causin... | rails, callback, atomicity | dual |

### False Positive

Clean code cases to test for over-detection.

#### FP - False Positive (13)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [FP_001](../cases/rails/FP_001/plan.md) | - | easy | standard_crud | false_positive, crud, baseline | semantic |
| [FP_002](../cases/rails/FP_002/plan.md) | - | easy | standard_validation | false_positive, validation, baseline | semantic |
| [FP_003](../cases/rails/FP_003/plan.md) | - | easy | standard_association | false_positive, association, baseline | semantic |
| [FP_004](../cases/rails/FP_004/plan.md) | - | easy | standard_scope | false_positive, scope, baseline | semantic |
| [FP_005](../cases/rails/FP_005/plan.md) | - | easy | standard_callback | false_positive, callback, baseline | semantic |
| [FP_006](../cases/rails/FP_006/plan.md) | - | medium | complex_nested_transaction | false_positive, transaction, complex | semantic |
| [FP_008](../cases/rails/FP_008/plan.md) | - | medium | complex_state_machine | false_positive, state, complex | semantic |
| [FP_011](../cases/rails/FP_011/plan.md) | - | medium | intentional_no_validation | false_positive, validation, intentional | semantic |
| [FP_012](../cases/rails/FP_012/plan.md) | - | medium | intentional_raw_sql | false_positive, sql, intentional | semantic |
| [FP_013](../cases/rails/FP_013/plan.md) | - | medium | intentional_update_all | false_positive, update_all, intentional | semantic |
| [FP_014](../cases/rails/FP_014/plan.md) | - | medium | benchmark_service | false_positive, service_object, batch_processing | semantic |
| [FP_016](../cases/rails/FP_016/plan.md) | - | hard | optimized_counter_cache | false_positive, optimization, counter_cache | semantic |
| [FP_018](../cases/rails/FP_018/plan.md) | - | hard | optimized_cache_warming | false_positive, optimization, cache | semantic |

## Laravel Cases

### Spec Alignment

Cases that test Plan vs Code alignment.

#### CALC - Price Calculation (10)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [CALC_001](../cases/laravel/CALC_001/plan.md) | critical | easy | Discount rate direction wrong, becomes 90% off | calculation, discount, member | semantic |
| [CALC_002](../cases/laravel/CALC_002/plan.md) | high | medium | Tax calculation order wrong - applying tax befo... | calculation, tax, discount | semantic |
| [CALC_003](../cases/laravel/CALC_003/plan.md) | medium | medium | Inconsistent rounding - round per item then sum... | calculation, rounding | semantic |
| [CALC_004](../cases/laravel/CALC_004/plan.md) | high | medium | Floating point precision error - 0.1 + 0.2 != 0... | calculation, currency, precision | semantic |
| [CALC_005](../cases/laravel/CALC_005/plan.md) | high | easy | Hardcoded old tax rate - still using 8% instead... | calculation, tax, hardcode | semantic |
| [CALC_006](../cases/laravel/CALC_006/plan.md) | medium | easy | Boundary condition error - >= 5000 vs > 5000 | calculation, shipping, boundary | semantic |
| [CALC_007](../cases/laravel/CALC_007/plan.md) | medium | medium | Points calculated on pre-discount amount instea... | calculation, points, discount | semantic |
| [CALC_008](../cases/laravel/CALC_008/plan.md) | high | medium | Coupon stacking allowed - multiple coupons can ... | calculation, coupon, validation | semantic |
| [CALC_009](../cases/laravel/CALC_009/plan.md) | medium | medium | Minimum check on pre-discount amount instead of... | calculation, validation, minimum | semantic |
| [CALC_010](../cases/laravel/CALC_010/plan.md) | critical | hard | Integer overflow on unit_price * quantity for l... | calculation, overflow, bulk | semantic |

#### STOCK - Inventory & Quantity (8)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [STOCK_001](../cases/laravel/STOCK_001/plan.md) | high | medium | Stock reserved at cart addition instead of chec... | inventory, timing, reservation | semantic |
| [STOCK_002](../cases/laravel/STOCK_002/plan.md) | critical | hard | Race condition between stock check and update | inventory, race_condition, atomic | semantic |
| [STOCK_003](../cases/laravel/STOCK_003/plan.md) | high | medium | Stock is restored when return is requested, not... | inventory, returns, workflow | semantic |
| [STOCK_004](../cases/laravel/STOCK_004/plan.md) | high | medium | Negative stock check only logs warning but does... | inventory, validation, negative_stock | semantic |
| [STOCK_005](../cases/laravel/STOCK_005/plan.md) | critical | hard | Bundle stock reservation is not atomic - race c... | inventory, bundle, race_condition | semantic |
| [STOCK_006](../cases/laravel/STOCK_006/plan.md) | high | medium | Available preorder slots calculated wrong - use... | inventory, preorder, calculation | semantic |
| [STOCK_007](../cases/laravel/STOCK_007/plan.md) | high | medium | Transfer stock check uses total quantity instea... | inventory, warehouse, reserved_stock | semantic |
| [STOCK_008](../cases/laravel/STOCK_008/plan.md) | high | medium | Reorder check and calculation use stock_quantit... | inventory, reorder, reserved_stock | semantic |

#### STATE - State Transitions (6)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [STATE_001](../cases/laravel/STATE_001/plan.md) | critical | medium | State transition validation is performed but re... | state_machine, validation, workflow | semantic |
| [STATE_002](../cases/laravel/STATE_002/plan.md) | high | easy | Subscription can be activated from any state, i... | state_machine, subscription, validation | semantic |
| [STATE_003](../cases/laravel/STATE_003/plan.md) | critical | medium | Refund can be initiated multiple times - 'refun... | state_machine, payment, refund | semantic |
| [STATE_004](../cases/laravel/STATE_004/plan.md) | high | easy | Articles can be published directly from pending... | state_machine, content, workflow | semantic |
| [STATE_005](../cases/laravel/STATE_005/plan.md) | medium | easy | Agent can be assigned to resolved/closed ticket... | state_machine, support, workflow | semantic |
| [STATE_006](../cases/laravel/STATE_006/plan.md) | high | hard | Recording interview result advances stage based... | state_machine, interview, workflow | semantic |

#### AUTH - Authorization (7)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [AUTH_001](../cases/laravel/AUTH_001/plan.md) | critical | easy | IDOR vulnerability - can access other user's or... | authorization, idor, security | semantic |
| [AUTH_002](../cases/laravel/AUTH_002/plan.md) | critical | easy | Can manipulate other user's cart by specifying ... | authorization, cart, security | semantic |
| [AUTH_003](../cases/laravel/AUTH_003/plan.md) | high | medium | Deleted user's order data still accessible in r... | authorization, deleted, privacy | semantic |
| [AUTH_004](../cases/laravel/AUTH_004/plan.md) | critical | easy | Regular users can change prices - admin check m... | authorization, admin, permission | semantic |
| [AUTH_005](../cases/laravel/AUTH_005/plan.md) | high | medium | Guest users getting member pricing - membership... | authorization, membership, pricing | semantic |
| [AUTH_006](../cases/laravel/AUTH_006/plan.md) | high | easy | Can access other user's points via API | authorization, points, api | semantic |
| [AUTH_007](../cases/laravel/AUTH_007/plan.md) | high | medium | Can use another user's personal coupon code | authorization, coupon, ownership | semantic |

#### TIME - Time & Duration (5)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [TIME_001](../cases/laravel/TIME_001/plan.md) | high | medium | Sale times parsed in local timezone but not con... | time, timezone, flash_sale | semantic |
| [TIME_002](../cases/laravel/TIME_002/plan.md) | medium | medium | Comparing datetime (now()) with date columns - ... | time, date, coupon | semantic |
| [TIME_003](../cases/laravel/TIME_003/plan.md) | high | hard | Past slot filtering uses server timezone (UTC) ... | time, timezone, booking | semantic |
| [TIME_004](../cases/laravel/TIME_004/plan.md) | high | medium | Setting day to 31 on a 30-day month causes date... | time, billing, date_overflow | semantic |
| [TIME_005](../cases/laravel/TIME_005/plan.md) | high | hard | Daily report queries UTC day boundaries instead... | time, timezone, reporting | semantic |

#### NOTIFY - Notifications (3)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [NOTIFY_001](../cases/laravel/NOTIFY_001/plan.md) | medium | easy | User notification preference is checked but not... | notification, preferences, email | semantic |
| [NOTIFY_002](../cases/laravel/NOTIFY_002/plan.md) | medium | medium | Alert timestamp updated before notification is ... | notification, alert, ordering | semantic |
| [NOTIFY_004](../cases/laravel/NOTIFY_004/plan.md) | medium | medium | Reminder sent immediately instead of scheduling... | notification, timezone, scheduling | semantic |

### Implicit Knowledge

Cases that test detection of issues not explicitly in Plan.

#### PERF - Performance (9)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [PERF_001](../cases/laravel/PERF_001/plan.md) | medium | easy | N+1 query problem - category loaded separately ... | performance, n+1, eager_loading | semantic |
| [PERF_002](../cases/laravel/PERF_002/plan.md) | high | medium | Nested N+1 queries - orders, items, and product... | performance, n+1, nested_relations | semantic |
| [PERF_003](../cases/laravel/PERF_003/plan.md) | high | medium | Multiple queries defeat index usage - leading w... | performance, indexing, query_optimization | semantic |
| [PERF_004](../cases/laravel/PERF_004/plan.md) | high | medium | Multiple separate queries instead of combined a... | performance, aggregation, database | semantic |
| [PERF_005](../cases/laravel/PERF_005/plan.md) | high | medium | Loads all records into memory for export instea... | performance, memory, export | semantic |
| [PERF_006](../cases/laravel/PERF_006/plan.md) | high | medium | Synchronous notification sending in loop blocks... | performance, notifications, async | semantic |
| [PERF_007](../cases/laravel/PERF_007/plan.md) | medium | medium | Multiple N+1 queries in cart: items, products, ... | performance, n+1, cart | semantic |
| [PERF_008](../cases/laravel/PERF_008/plan.md) | high | easy | Individual SELECT/UPDATE/INSERT operations in l... | performance, bulk_operations, database | semantic |
| [PERF_009](../cases/laravel/PERF_009/plan.md) | high | hard | Cache stampede vulnerability plus N+1 queries o... | performance, cache, stampede | semantic |

### False Positive

Clean code cases to test for over-detection.

#### FP - False Positive (10)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [FP_001](../cases/laravel/FP_001/plan.md) | - | easy | standard_crud | false_positive, crud, baseline | semantic |
| [FP_002](../cases/laravel/FP_002/plan.md) | - | easy | order_processing | false_positive, order, transaction | semantic |
| [FP_003](../cases/laravel/FP_003/plan.md) | - | easy | product_search | false_positive, search, filter | semantic |
| [FP_004](../cases/laravel/FP_004/plan.md) | - | easy | notification_service | false_positive, notification, email | semantic |
| [FP_005](../cases/laravel/FP_005/plan.md) | - | easy | authentication_service | false_positive, authentication, security | semantic |
| [FP_006](../cases/laravel/FP_006/plan.md) | - | easy | inventory_management_service | false_positive, inventory, concurrency | semantic |
| [FP_007](../cases/laravel/FP_007/plan.md) | - | easy | rate_limit_service | false_positive, rate_limiting, cache | semantic |
| [FP_008](../cases/laravel/FP_008/plan.md) | - | easy | file_upload_service | false_positive, file_upload, security | semantic |
| [FP_009](../cases/laravel/FP_009/plan.md) | - | easy | audit_logging_service | false_positive, audit, logging | semantic |
| [FP_010](../cases/laravel/FP_010/plan.md) | - | medium | payment_webhook_handler | false_positive, webhook, payment | semantic |

## Django Cases

### Spec Alignment

Cases that test Plan vs Code alignment.

#### CALC - Price Calculation (10)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [CALC_001](../cases/django/CALC_001/plan.md) | critical | easy | Discount rate direction wrong, becomes 90% off | calculation, discount, member | severity |
| [CALC_002](../cases/django/CALC_002/plan.md) | high | medium | Tax calculation order wrong - applying tax befo... | calculation, tax, discount | severity |
| [CALC_003](../cases/django/CALC_003/plan.md) | high | medium | Floating point precision error - 0.1 + 0.2 != 0... | calculation, currency, precision | severity |
| [CALC_004](../cases/django/CALC_004/plan.md) | medium | medium | Inconsistent rounding - round per item then sum... | calculation, rounding | severity |
| [CALC_005](../cases/django/CALC_005/plan.md) | high | easy | Hardcoded old tax rate - still using 8% instead... | calculation, tax, hardcode | severity |
| [CALC_006](../cases/django/CALC_006/plan.md) | medium | easy | Boundary condition error - >= 5000 vs > 5000 | calculation, shipping, boundary | severity |
| [CALC_007](../cases/django/CALC_007/plan.md) | medium | medium | Points calculated on pre-discount amount instea... | calculation, points, discount | severity |
| [CALC_008](../cases/django/CALC_008/plan.md) | high | medium | Coupon stacking allowed - multiple coupons can ... | calculation, coupon, validation | severity |
| [CALC_009](../cases/django/CALC_009/plan.md) | medium | medium | Minimum check on pre-discount amount instead of... | calculation, validation, minimum | severity |
| [CALC_010](../cases/django/CALC_010/plan.md) | critical | hard | Integer overflow on unit_price * quantity for l... | calculation, overflow, bulk | severity |

#### AUTH - Authorization (7)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [AUTH_001](../cases/django/AUTH_001/plan.md) | critical | easy | IDOR vulnerability - can access other user's or... | authorization, idor, security | severity |
| [AUTH_002](../cases/django/AUTH_002/plan.md) | critical | easy | Can manipulate other user's cart by specifying ... | authorization, cart, security | severity |
| [AUTH_003](../cases/django/AUTH_003/plan.md) | high | medium | Deleted user's order data still accessible | authorization, deleted, privacy | severity |
| [AUTH_004](../cases/django/AUTH_004/plan.md) | critical | easy | Regular users can change prices - admin check m... | authorization, admin, permission | severity |
| [AUTH_005](../cases/django/AUTH_005/plan.md) | high | medium | Guest users getting member pricing - membership... | authorization, membership, pricing | severity |
| [AUTH_006](../cases/django/AUTH_006/plan.md) | high | easy | Can access other user's points via API | authorization, points, api | severity |
| [AUTH_007](../cases/django/AUTH_007/plan.md) | high | medium | Can use another user's coupon code | authorization, coupon, ownership | severity |

### Implicit Knowledge

Cases that test detection of issues not explicitly in Plan.

#### DJANGO - Django-Specific (8)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [DJANGO_001](../cases/django/DJANGO_001/plan.md) | medium | easy | QuerySet method not used - reimplementing filte... | django, orm, dry | severity |
| [DJANGO_002](../cases/django/DJANGO_002/plan.md) | high | medium | Wrong eager loading method - select_related for... | django, orm, performance | severity |
| [DJANGO_003](../cases/django/DJANGO_003/plan.md) | high | medium | QuerySet.update() skips save() hooks and signals | django, orm, hooks | severity |
| [DJANGO_004](../cases/django/DJANGO_004/plan.md) | high | medium | post_save signal fires on update - missing crea... | django, signal, conditional | severity |
| [DJANGO_005](../cases/django/DJANGO_005/plan.md) | critical | medium | Task queued inside transaction - runs even on r... | django, signal, transaction | severity |
| [DJANGO_006](../cases/django/DJANGO_006/plan.md) | critical | easy | View accessible without login - missing @login_... | django, security, authentication | severity |
| [DJANGO_007](../cases/django/DJANGO_007/plan.md) | critical | easy | SQL injection via f-string in raw query | django, security, sql_injection | severity |
| [DJANGO_008](../cases/django/DJANGO_008/plan.md) | critical | hard | Permission check before auth middleware - user ... | django, middleware, order | severity |

### False Positive

Clean code cases to test for over-detection.

#### FP - False Positive (5)

| Case ID | Severity | Difficulty | Description | Tags | Mode |
|---------|----------|------------|-------------|------|------|
| [FP_001](../cases/django/FP_001/plan.md) | - | easy | standard_crud | false_positive, crud, baseline | severity |
| [FP_002](../cases/django/FP_002/plan.md) | - | easy | standard_model_validation | false_positive, validation, baseline | severity |
| [FP_003](../cases/django/FP_003/plan.md) | - | easy | standard_queryset | false_positive, queryset, baseline | severity |
| [FP_004](../cases/django/FP_004/plan.md) | - | medium | intentional_raw_sql | false_positive, sql, intentional | severity |
| [FP_005](../cases/django/FP_005/plan.md) | - | medium | intentional_update_bulk | false_positive, bulk_update, intentional | severity |

## Indexes

### By Severity

**critical** (44): [AUTH_001](../cases/django/AUTH_001/plan.md), [AUTH_001](../cases/laravel/AUTH_001/plan.md), [AUTH_001](../cases/rails/AUTH_001/plan.md), [AUTH_002](../cases/django/AUTH_002/plan.md), [AUTH_002](../cases/laravel/AUTH_002/plan.md), [AUTH_002](../cases/rails/AUTH_002/plan.md), [AUTH_004](../cases/django/AUTH_004/plan.md), [AUTH_004](../cases/laravel/AUTH_004/plan.md), [AUTH_004](../cases/rails/AUTH_004/plan.md), [AUTH_008](../cases/rails/AUTH_008/plan.md), [CALC_001](../cases/django/CALC_001/plan.md), [CALC_001](../cases/laravel/CALC_001/plan.md), [CALC_001](../cases/rails/CALC_001/plan.md), [CALC_010](../cases/django/CALC_010/plan.md), [CALC_010](../cases/laravel/CALC_010/plan.md), [CALC_010](../cases/rails/CALC_010/plan.md), [CALC_011](../cases/rails/CALC_011/plan.md), [DATA_002](../cases/rails/DATA_002/plan.md), [DJANGO_005](../cases/django/DJANGO_005/plan.md), [DJANGO_006](../cases/django/DJANGO_006/plan.md), [DJANGO_007](../cases/django/DJANGO_007/plan.md), [DJANGO_008](../cases/django/DJANGO_008/plan.md), [EXT_001](../cases/rails/EXT_001/plan.md), [EXT_002](../cases/rails/EXT_002/plan.md), [EXT_003](../cases/rails/EXT_003/plan.md), [EXT_004](../cases/rails/EXT_004/plan.md), [EXT_007](../cases/rails/EXT_007/plan.md), [NOTIFY_005](../cases/rails/NOTIFY_005/plan.md), [PERF_002](../cases/rails/PERF_002/plan.md), [RAILS_005](../cases/rails/RAILS_005/plan.md), [RAILS_006](../cases/rails/RAILS_006/plan.md), [RAILS_011](../cases/rails/RAILS_011/plan.md), [RAILS_012](../cases/rails/RAILS_012/plan.md), [RAILS_013](../cases/rails/RAILS_013/plan.md), [STATE_001](../cases/laravel/STATE_001/plan.md), [STATE_001](../cases/rails/STATE_001/plan.md), [STATE_003](../cases/laravel/STATE_003/plan.md), [STATE_003](../cases/rails/STATE_003/plan.md), [STATE_004](../cases/rails/STATE_004/plan.md), [STOCK_002](../cases/laravel/STOCK_002/plan.md), [STOCK_002](../cases/rails/STOCK_002/plan.md), [STOCK_004](../cases/rails/STOCK_004/plan.md), [STOCK_005](../cases/laravel/STOCK_005/plan.md), [STOCK_007](../cases/rails/STOCK_007/plan.md)

**high** (79): [AUTH_003](../cases/django/AUTH_003/plan.md), [AUTH_003](../cases/laravel/AUTH_003/plan.md), [AUTH_003](../cases/rails/AUTH_003/plan.md), [AUTH_005](../cases/django/AUTH_005/plan.md), [AUTH_005](../cases/laravel/AUTH_005/plan.md), [AUTH_005](../cases/rails/AUTH_005/plan.md), [AUTH_006](../cases/django/AUTH_006/plan.md), [AUTH_006](../cases/laravel/AUTH_006/plan.md), [AUTH_006](../cases/rails/AUTH_006/plan.md), [AUTH_007](../cases/django/AUTH_007/plan.md), [AUTH_007](../cases/laravel/AUTH_007/plan.md), [AUTH_007](../cases/rails/AUTH_007/plan.md), [CALC_002](../cases/django/CALC_002/plan.md), [CALC_002](../cases/laravel/CALC_002/plan.md), [CALC_002](../cases/rails/CALC_002/plan.md), [CALC_003](../cases/django/CALC_003/plan.md), [CALC_004](../cases/laravel/CALC_004/plan.md), [CALC_004](../cases/rails/CALC_004/plan.md), [CALC_005](../cases/django/CALC_005/plan.md), [CALC_005](../cases/laravel/CALC_005/plan.md), [CALC_005](../cases/rails/CALC_005/plan.md), [CALC_008](../cases/django/CALC_008/plan.md), [CALC_008](../cases/laravel/CALC_008/plan.md), [CALC_008](../cases/rails/CALC_008/plan.md), [DATA_001](../cases/rails/DATA_001/plan.md), [DATA_003](../cases/rails/DATA_003/plan.md), [DATA_004](../cases/rails/DATA_004/plan.md), [DATA_007](../cases/rails/DATA_007/plan.md), [DJANGO_002](../cases/django/DJANGO_002/plan.md), [DJANGO_003](../cases/django/DJANGO_003/plan.md), [DJANGO_004](../cases/django/DJANGO_004/plan.md), [EXT_005](../cases/rails/EXT_005/plan.md), [EXT_006](../cases/rails/EXT_006/plan.md), [NOTIFY_001](../cases/rails/NOTIFY_001/plan.md), [NOTIFY_002](../cases/rails/NOTIFY_002/plan.md), [NOTIFY_003](../cases/laravel/NOTIFY_003/plan.md), [NOTIFY_003](../cases/rails/NOTIFY_003/plan.md), [PERF_001](../cases/rails/PERF_001/plan.md), [PERF_002](../cases/laravel/PERF_002/plan.md), [PERF_003](../cases/laravel/PERF_003/plan.md), [PERF_004](../cases/laravel/PERF_004/plan.md), [PERF_005](../cases/laravel/PERF_005/plan.md), [PERF_005](../cases/rails/PERF_005/plan.md), [PERF_006](../cases/laravel/PERF_006/plan.md), [PERF_006](../cases/rails/PERF_006/plan.md), [PERF_007](../cases/rails/PERF_007/plan.md), [PERF_008](../cases/laravel/PERF_008/plan.md), [PERF_008](../cases/rails/PERF_008/plan.md), [PERF_009](../cases/laravel/PERF_009/plan.md), [RAILS_003](../cases/rails/RAILS_003/plan.md), [RAILS_004](../cases/rails/RAILS_004/plan.md), [RAILS_007](../cases/rails/RAILS_007/plan.md), [RAILS_008](../cases/rails/RAILS_008/plan.md), [RAILS_014](../cases/rails/RAILS_014/plan.md), [RAILS_015](../cases/rails/RAILS_015/plan.md), [RAILS_016](../cases/rails/RAILS_016/plan.md), [STATE_002](../cases/laravel/STATE_002/plan.md), [STATE_002](../cases/rails/STATE_002/plan.md), [STATE_004](../cases/laravel/STATE_004/plan.md), [STATE_005](../cases/rails/STATE_005/plan.md), [STATE_006](../cases/laravel/STATE_006/plan.md), [STATE_006](../cases/rails/STATE_006/plan.md), [STOCK_001](../cases/laravel/STOCK_001/plan.md), [STOCK_001](../cases/rails/STOCK_001/plan.md), [STOCK_003](../cases/laravel/STOCK_003/plan.md), [STOCK_003](../cases/rails/STOCK_003/plan.md), [STOCK_004](../cases/laravel/STOCK_004/plan.md), [STOCK_006](../cases/laravel/STOCK_006/plan.md), [STOCK_006](../cases/rails/STOCK_006/plan.md), [STOCK_007](../cases/laravel/STOCK_007/plan.md), [STOCK_008](../cases/laravel/STOCK_008/plan.md), [STOCK_008](../cases/rails/STOCK_008/plan.md), [TIME_001](../cases/laravel/TIME_001/plan.md), [TIME_002](../cases/rails/TIME_002/plan.md), [TIME_003](../cases/laravel/TIME_003/plan.md), [TIME_004](../cases/laravel/TIME_004/plan.md), [TIME_005](../cases/laravel/TIME_005/plan.md), [TIME_005](../cases/rails/TIME_005/plan.md), [TIME_006](../cases/rails/TIME_006/plan.md)

**medium** (38): [CALC_003](../cases/laravel/CALC_003/plan.md), [CALC_003](../cases/rails/CALC_003/plan.md), [CALC_004](../cases/django/CALC_004/plan.md), [CALC_006](../cases/django/CALC_006/plan.md), [CALC_006](../cases/laravel/CALC_006/plan.md), [CALC_006](../cases/rails/CALC_006/plan.md), [CALC_007](../cases/django/CALC_007/plan.md), [CALC_007](../cases/laravel/CALC_007/plan.md), [CALC_007](../cases/rails/CALC_007/plan.md), [CALC_009](../cases/django/CALC_009/plan.md), [CALC_009](../cases/laravel/CALC_009/plan.md), [CALC_009](../cases/rails/CALC_009/plan.md), [DATA_005](../cases/rails/DATA_005/plan.md), [DATA_006](../cases/rails/DATA_006/plan.md), [DJANGO_001](../cases/django/DJANGO_001/plan.md), [NOTIFY_001](../cases/laravel/NOTIFY_001/plan.md), [NOTIFY_002](../cases/laravel/NOTIFY_002/plan.md), [NOTIFY_004](../cases/laravel/NOTIFY_004/plan.md), [NOTIFY_004](../cases/rails/NOTIFY_004/plan.md), [NOTIFY_006](../cases/rails/NOTIFY_006/plan.md), [PERF_001](../cases/laravel/PERF_001/plan.md), [PERF_003](../cases/rails/PERF_003/plan.md), [PERF_004](../cases/rails/PERF_004/plan.md), [PERF_007](../cases/laravel/PERF_007/plan.md), [RAILS_001](../cases/rails/RAILS_001/plan.md), [RAILS_002](../cases/rails/RAILS_002/plan.md), [RAILS_009](../cases/rails/RAILS_009/plan.md), [RAILS_010](../cases/rails/RAILS_010/plan.md), [STATE_005](../cases/laravel/STATE_005/plan.md), [STATE_007](../cases/rails/STATE_007/plan.md), [STOCK_005](../cases/rails/STOCK_005/plan.md), [TIME_001](../cases/rails/TIME_001/plan.md), [TIME_002](../cases/laravel/TIME_002/plan.md), [TIME_003](../cases/rails/TIME_003/plan.md), [TIME_004](../cases/rails/TIME_004/plan.md), [TIME_006](../cases/laravel/TIME_006/plan.md), [TIME_007](../cases/rails/TIME_007/plan.md), [TIME_008](../cases/rails/TIME_008/plan.md)

### By Difficulty

**easy** (63): [AUTH_001](../cases/django/AUTH_001/plan.md), [AUTH_001](../cases/laravel/AUTH_001/plan.md), [AUTH_001](../cases/rails/AUTH_001/plan.md), [AUTH_002](../cases/django/AUTH_002/plan.md), [AUTH_002](../cases/laravel/AUTH_002/plan.md), [AUTH_002](../cases/rails/AUTH_002/plan.md), [AUTH_004](../cases/django/AUTH_004/plan.md), [AUTH_004](../cases/laravel/AUTH_004/plan.md), [AUTH_004](../cases/rails/AUTH_004/plan.md), [AUTH_006](../cases/django/AUTH_006/plan.md), [AUTH_006](../cases/laravel/AUTH_006/plan.md), [AUTH_006](../cases/rails/AUTH_006/plan.md), [CALC_001](../cases/django/CALC_001/plan.md), [CALC_001](../cases/laravel/CALC_001/plan.md), [CALC_001](../cases/rails/CALC_001/plan.md), [CALC_005](../cases/django/CALC_005/plan.md), [CALC_005](../cases/laravel/CALC_005/plan.md), [CALC_005](../cases/rails/CALC_005/plan.md), [CALC_006](../cases/django/CALC_006/plan.md), [CALC_006](../cases/laravel/CALC_006/plan.md), [CALC_006](../cases/rails/CALC_006/plan.md), [DATA_002](../cases/rails/DATA_002/plan.md), [DATA_004](../cases/rails/DATA_004/plan.md), [DJANGO_001](../cases/django/DJANGO_001/plan.md), [DJANGO_006](../cases/django/DJANGO_006/plan.md), [DJANGO_007](../cases/django/DJANGO_007/plan.md), [FP_001](../cases/django/FP_001/plan.md), [FP_001](../cases/laravel/FP_001/plan.md), [FP_001](../cases/rails/FP_001/plan.md), [FP_002](../cases/django/FP_002/plan.md), [FP_002](../cases/laravel/FP_002/plan.md), [FP_002](../cases/rails/FP_002/plan.md), [FP_003](../cases/django/FP_003/plan.md), [FP_003](../cases/laravel/FP_003/plan.md), [FP_003](../cases/rails/FP_003/plan.md), [FP_004](../cases/laravel/FP_004/plan.md), [FP_004](../cases/rails/FP_004/plan.md), [FP_005](../cases/laravel/FP_005/plan.md), [FP_005](../cases/rails/FP_005/plan.md), [FP_006](../cases/laravel/FP_006/plan.md), [FP_007](../cases/laravel/FP_007/plan.md), [FP_008](../cases/laravel/FP_008/plan.md), [FP_009](../cases/laravel/FP_009/plan.md), [NOTIFY_001](../cases/laravel/NOTIFY_001/plan.md), [NOTIFY_004](../cases/rails/NOTIFY_004/plan.md), [PERF_001](../cases/laravel/PERF_001/plan.md), [PERF_001](../cases/rails/PERF_001/plan.md), [PERF_002](../cases/rails/PERF_002/plan.md), [PERF_004](../cases/rails/PERF_004/plan.md), [PERF_008](../cases/laravel/PERF_008/plan.md), [RAILS_001](../cases/rails/RAILS_001/plan.md), [RAILS_002](../cases/rails/RAILS_002/plan.md), [RAILS_004](../cases/rails/RAILS_004/plan.md), [RAILS_006](../cases/rails/RAILS_006/plan.md), [RAILS_009](../cases/rails/RAILS_009/plan.md), [STATE_002](../cases/laravel/STATE_002/plan.md), [STATE_002](../cases/rails/STATE_002/plan.md), [STATE_004](../cases/laravel/STATE_004/plan.md), [STATE_005](../cases/laravel/STATE_005/plan.md), [STATE_006](../cases/rails/STATE_006/plan.md), [STOCK_005](../cases/rails/STOCK_005/plan.md), [TIME_003](../cases/rails/TIME_003/plan.md), [TIME_008](../cases/rails/TIME_008/plan.md)

**hard** (32): [CALC_010](../cases/django/CALC_010/plan.md), [CALC_010](../cases/laravel/CALC_010/plan.md), [CALC_010](../cases/rails/CALC_010/plan.md), [DATA_005](../cases/rails/DATA_005/plan.md), [DATA_007](../cases/rails/DATA_007/plan.md), [DJANGO_008](../cases/django/DJANGO_008/plan.md), [EXT_001](../cases/rails/EXT_001/plan.md), [EXT_003](../cases/rails/EXT_003/plan.md), [EXT_004](../cases/rails/EXT_004/plan.md), [EXT_005](../cases/rails/EXT_005/plan.md), [EXT_007](../cases/rails/EXT_007/plan.md), [FP_016](../cases/rails/FP_016/plan.md), [FP_018](../cases/rails/FP_018/plan.md), [PERF_008](../cases/rails/PERF_008/plan.md), [PERF_009](../cases/laravel/PERF_009/plan.md), [RAILS_003](../cases/rails/RAILS_003/plan.md), [RAILS_007](../cases/rails/RAILS_007/plan.md), [RAILS_010](../cases/rails/RAILS_010/plan.md), [RAILS_011](../cases/rails/RAILS_011/plan.md), [RAILS_012](../cases/rails/RAILS_012/plan.md), [RAILS_013](../cases/rails/RAILS_013/plan.md), [STATE_004](../cases/rails/STATE_004/plan.md), [STATE_006](../cases/laravel/STATE_006/plan.md), [STOCK_002](../cases/laravel/STOCK_002/plan.md), [STOCK_002](../cases/rails/STOCK_002/plan.md), [STOCK_005](../cases/laravel/STOCK_005/plan.md), [STOCK_008](../cases/rails/STOCK_008/plan.md), [TIME_003](../cases/laravel/TIME_003/plan.md), [TIME_005](../cases/laravel/TIME_005/plan.md), [TIME_005](../cases/rails/TIME_005/plan.md), [TIME_006](../cases/laravel/TIME_006/plan.md), [TIME_006](../cases/rails/TIME_006/plan.md)

**medium** (94): [AUTH_003](../cases/django/AUTH_003/plan.md), [AUTH_003](../cases/laravel/AUTH_003/plan.md), [AUTH_003](../cases/rails/AUTH_003/plan.md), [AUTH_005](../cases/django/AUTH_005/plan.md), [AUTH_005](../cases/laravel/AUTH_005/plan.md), [AUTH_005](../cases/rails/AUTH_005/plan.md), [AUTH_007](../cases/django/AUTH_007/plan.md), [AUTH_007](../cases/laravel/AUTH_007/plan.md), [AUTH_007](../cases/rails/AUTH_007/plan.md), [AUTH_008](../cases/rails/AUTH_008/plan.md), [CALC_002](../cases/django/CALC_002/plan.md), [CALC_002](../cases/laravel/CALC_002/plan.md), [CALC_002](../cases/rails/CALC_002/plan.md), [CALC_003](../cases/django/CALC_003/plan.md), [CALC_003](../cases/laravel/CALC_003/plan.md), [CALC_003](../cases/rails/CALC_003/plan.md), [CALC_004](../cases/django/CALC_004/plan.md), [CALC_004](../cases/laravel/CALC_004/plan.md), [CALC_004](../cases/rails/CALC_004/plan.md), [CALC_007](../cases/django/CALC_007/plan.md), [CALC_007](../cases/laravel/CALC_007/plan.md), [CALC_007](../cases/rails/CALC_007/plan.md), [CALC_008](../cases/django/CALC_008/plan.md), [CALC_008](../cases/laravel/CALC_008/plan.md), [CALC_008](../cases/rails/CALC_008/plan.md), [CALC_009](../cases/django/CALC_009/plan.md), [CALC_009](../cases/laravel/CALC_009/plan.md), [CALC_009](../cases/rails/CALC_009/plan.md), [CALC_011](../cases/rails/CALC_011/plan.md), [DATA_001](../cases/rails/DATA_001/plan.md), [DATA_003](../cases/rails/DATA_003/plan.md), [DATA_006](../cases/rails/DATA_006/plan.md), [DJANGO_002](../cases/django/DJANGO_002/plan.md), [DJANGO_003](../cases/django/DJANGO_003/plan.md), [DJANGO_004](../cases/django/DJANGO_004/plan.md), [DJANGO_005](../cases/django/DJANGO_005/plan.md), [EXT_002](../cases/rails/EXT_002/plan.md), [EXT_006](../cases/rails/EXT_006/plan.md), [FP_004](../cases/django/FP_004/plan.md), [FP_005](../cases/django/FP_005/plan.md), [FP_006](../cases/rails/FP_006/plan.md), [FP_008](../cases/rails/FP_008/plan.md), [FP_010](../cases/laravel/FP_010/plan.md), [FP_011](../cases/rails/FP_011/plan.md), [FP_012](../cases/rails/FP_012/plan.md), [FP_013](../cases/rails/FP_013/plan.md), [FP_014](../cases/rails/FP_014/plan.md), [NOTIFY_001](../cases/rails/NOTIFY_001/plan.md), [NOTIFY_002](../cases/laravel/NOTIFY_002/plan.md), [NOTIFY_002](../cases/rails/NOTIFY_002/plan.md), [NOTIFY_003](../cases/laravel/NOTIFY_003/plan.md), [NOTIFY_003](../cases/rails/NOTIFY_003/plan.md), [NOTIFY_004](../cases/laravel/NOTIFY_004/plan.md), [NOTIFY_005](../cases/rails/NOTIFY_005/plan.md), [NOTIFY_006](../cases/rails/NOTIFY_006/plan.md), [PERF_002](../cases/laravel/PERF_002/plan.md), [PERF_003](../cases/laravel/PERF_003/plan.md), [PERF_003](../cases/rails/PERF_003/plan.md), [PERF_004](../cases/laravel/PERF_004/plan.md), [PERF_005](../cases/laravel/PERF_005/plan.md), [PERF_005](../cases/rails/PERF_005/plan.md), [PERF_006](../cases/laravel/PERF_006/plan.md), [PERF_006](../cases/rails/PERF_006/plan.md), [PERF_007](../cases/laravel/PERF_007/plan.md), [PERF_007](../cases/rails/PERF_007/plan.md), [RAILS_005](../cases/rails/RAILS_005/plan.md), [RAILS_008](../cases/rails/RAILS_008/plan.md), [RAILS_014](../cases/rails/RAILS_014/plan.md), [RAILS_015](../cases/rails/RAILS_015/plan.md), [RAILS_016](../cases/rails/RAILS_016/plan.md), [STATE_001](../cases/laravel/STATE_001/plan.md), [STATE_001](../cases/rails/STATE_001/plan.md), [STATE_003](../cases/laravel/STATE_003/plan.md), [STATE_003](../cases/rails/STATE_003/plan.md), [STATE_005](../cases/rails/STATE_005/plan.md), [STATE_007](../cases/rails/STATE_007/plan.md), [STOCK_001](../cases/laravel/STOCK_001/plan.md), [STOCK_001](../cases/rails/STOCK_001/plan.md), [STOCK_003](../cases/laravel/STOCK_003/plan.md), [STOCK_003](../cases/rails/STOCK_003/plan.md), [STOCK_004](../cases/laravel/STOCK_004/plan.md), [STOCK_004](../cases/rails/STOCK_004/plan.md), [STOCK_006](../cases/laravel/STOCK_006/plan.md), [STOCK_006](../cases/rails/STOCK_006/plan.md), [STOCK_007](../cases/laravel/STOCK_007/plan.md), [STOCK_007](../cases/rails/STOCK_007/plan.md), [STOCK_008](../cases/laravel/STOCK_008/plan.md), [TIME_001](../cases/laravel/TIME_001/plan.md), [TIME_001](../cases/rails/TIME_001/plan.md), [TIME_002](../cases/laravel/TIME_002/plan.md), [TIME_002](../cases/rails/TIME_002/plan.md), [TIME_004](../cases/laravel/TIME_004/plan.md), [TIME_004](../cases/rails/TIME_004/plan.md), [TIME_007](../cases/rails/TIME_007/plan.md)

### By Evaluation Mode

**dual** (36): [AUTH_008](../cases/rails/AUTH_008/plan.md), [CALC_011](../cases/rails/CALC_011/plan.md), [DATA_001](../cases/rails/DATA_001/plan.md), [DATA_002](../cases/rails/DATA_002/plan.md), [DATA_003](../cases/rails/DATA_003/plan.md), [DATA_004](../cases/rails/DATA_004/plan.md), [DATA_005](../cases/rails/DATA_005/plan.md), [DATA_006](../cases/rails/DATA_006/plan.md), [DATA_007](../cases/rails/DATA_007/plan.md), [EXT_001](../cases/rails/EXT_001/plan.md), [EXT_002](../cases/rails/EXT_002/plan.md), [EXT_003](../cases/rails/EXT_003/plan.md), [EXT_004](../cases/rails/EXT_004/plan.md), [EXT_005](../cases/rails/EXT_005/plan.md), [EXT_006](../cases/rails/EXT_006/plan.md), [EXT_007](../cases/rails/EXT_007/plan.md), [PERF_001](../cases/rails/PERF_001/plan.md), [PERF_002](../cases/rails/PERF_002/plan.md), [PERF_003](../cases/rails/PERF_003/plan.md), [PERF_004](../cases/rails/PERF_004/plan.md), [PERF_005](../cases/rails/PERF_005/plan.md), [PERF_006](../cases/rails/PERF_006/plan.md), [PERF_007](../cases/rails/PERF_007/plan.md), [PERF_008](../cases/rails/PERF_008/plan.md), [RAILS_001](../cases/rails/RAILS_001/plan.md), [RAILS_002](../cases/rails/RAILS_002/plan.md), [RAILS_003](../cases/rails/RAILS_003/plan.md), [RAILS_004](../cases/rails/RAILS_004/plan.md), [RAILS_005](../cases/rails/RAILS_005/plan.md), [RAILS_006](../cases/rails/RAILS_006/plan.md), [RAILS_007](../cases/rails/RAILS_007/plan.md), [RAILS_008](../cases/rails/RAILS_008/plan.md), [RAILS_009](../cases/rails/RAILS_009/plan.md), [RAILS_010](../cases/rails/RAILS_010/plan.md), [RAILS_011](../cases/rails/RAILS_011/plan.md), [RAILS_016](../cases/rails/RAILS_016/plan.md)

**semantic** (119): [AUTH_001](../cases/laravel/AUTH_001/plan.md), [AUTH_001](../cases/rails/AUTH_001/plan.md), [AUTH_002](../cases/laravel/AUTH_002/plan.md), [AUTH_002](../cases/rails/AUTH_002/plan.md), [AUTH_003](../cases/laravel/AUTH_003/plan.md), [AUTH_003](../cases/rails/AUTH_003/plan.md), [AUTH_004](../cases/laravel/AUTH_004/plan.md), [AUTH_004](../cases/rails/AUTH_004/plan.md), [AUTH_005](../cases/laravel/AUTH_005/plan.md), [AUTH_005](../cases/rails/AUTH_005/plan.md), [AUTH_006](../cases/laravel/AUTH_006/plan.md), [AUTH_006](../cases/rails/AUTH_006/plan.md), [AUTH_007](../cases/laravel/AUTH_007/plan.md), [AUTH_007](../cases/rails/AUTH_007/plan.md), [CALC_001](../cases/laravel/CALC_001/plan.md), [CALC_001](../cases/rails/CALC_001/plan.md), [CALC_002](../cases/laravel/CALC_002/plan.md), [CALC_002](../cases/rails/CALC_002/plan.md), [CALC_003](../cases/laravel/CALC_003/plan.md), [CALC_003](../cases/rails/CALC_003/plan.md), [CALC_004](../cases/laravel/CALC_004/plan.md), [CALC_004](../cases/rails/CALC_004/plan.md), [CALC_005](../cases/laravel/CALC_005/plan.md), [CALC_005](../cases/rails/CALC_005/plan.md), [CALC_006](../cases/laravel/CALC_006/plan.md), [CALC_006](../cases/rails/CALC_006/plan.md), [CALC_007](../cases/laravel/CALC_007/plan.md), [CALC_007](../cases/rails/CALC_007/plan.md), [CALC_008](../cases/laravel/CALC_008/plan.md), [CALC_008](../cases/rails/CALC_008/plan.md), [CALC_009](../cases/laravel/CALC_009/plan.md), [CALC_009](../cases/rails/CALC_009/plan.md), [CALC_010](../cases/laravel/CALC_010/plan.md), [CALC_010](../cases/rails/CALC_010/plan.md), [FP_001](../cases/laravel/FP_001/plan.md), [FP_001](../cases/rails/FP_001/plan.md), [FP_002](../cases/laravel/FP_002/plan.md), [FP_002](../cases/rails/FP_002/plan.md), [FP_003](../cases/laravel/FP_003/plan.md), [FP_003](../cases/rails/FP_003/plan.md), [FP_004](../cases/laravel/FP_004/plan.md), [FP_004](../cases/rails/FP_004/plan.md), [FP_005](../cases/laravel/FP_005/plan.md), [FP_005](../cases/rails/FP_005/plan.md), [FP_006](../cases/laravel/FP_006/plan.md), [FP_006](../cases/rails/FP_006/plan.md), [FP_007](../cases/laravel/FP_007/plan.md), [FP_008](../cases/laravel/FP_008/plan.md), [FP_008](../cases/rails/FP_008/plan.md), [FP_009](../cases/laravel/FP_009/plan.md), [FP_010](../cases/laravel/FP_010/plan.md), [FP_011](../cases/rails/FP_011/plan.md), [FP_012](../cases/rails/FP_012/plan.md), [FP_013](../cases/rails/FP_013/plan.md), [FP_014](../cases/rails/FP_014/plan.md), [FP_016](../cases/rails/FP_016/plan.md), [FP_018](../cases/rails/FP_018/plan.md), [NOTIFY_001](../cases/laravel/NOTIFY_001/plan.md), [NOTIFY_001](../cases/rails/NOTIFY_001/plan.md), [NOTIFY_002](../cases/laravel/NOTIFY_002/plan.md), [NOTIFY_002](../cases/rails/NOTIFY_002/plan.md), [NOTIFY_003](../cases/laravel/NOTIFY_003/plan.md), [NOTIFY_003](../cases/rails/NOTIFY_003/plan.md), [NOTIFY_004](../cases/laravel/NOTIFY_004/plan.md), [NOTIFY_004](../cases/rails/NOTIFY_004/plan.md), [NOTIFY_005](../cases/rails/NOTIFY_005/plan.md), [NOTIFY_006](../cases/rails/NOTIFY_006/plan.md), [PERF_001](../cases/laravel/PERF_001/plan.md), [PERF_002](../cases/laravel/PERF_002/plan.md), [PERF_003](../cases/laravel/PERF_003/plan.md), [PERF_004](../cases/laravel/PERF_004/plan.md), [PERF_005](../cases/laravel/PERF_005/plan.md), [PERF_006](../cases/laravel/PERF_006/plan.md), [PERF_007](../cases/laravel/PERF_007/plan.md), [PERF_008](../cases/laravel/PERF_008/plan.md), [PERF_009](../cases/laravel/PERF_009/plan.md), [STATE_001](../cases/laravel/STATE_001/plan.md), [STATE_001](../cases/rails/STATE_001/plan.md), [STATE_002](../cases/laravel/STATE_002/plan.md), [STATE_002](../cases/rails/STATE_002/plan.md), [STATE_003](../cases/laravel/STATE_003/plan.md), [STATE_003](../cases/rails/STATE_003/plan.md), [STATE_004](../cases/laravel/STATE_004/plan.md), [STATE_004](../cases/rails/STATE_004/plan.md), [STATE_005](../cases/laravel/STATE_005/plan.md), [STATE_005](../cases/rails/STATE_005/plan.md), [STATE_006](../cases/laravel/STATE_006/plan.md), [STATE_006](../cases/rails/STATE_006/plan.md), [STATE_007](../cases/rails/STATE_007/plan.md), [STOCK_001](../cases/laravel/STOCK_001/plan.md), [STOCK_001](../cases/rails/STOCK_001/plan.md), [STOCK_002](../cases/laravel/STOCK_002/plan.md), [STOCK_002](../cases/rails/STOCK_002/plan.md), [STOCK_003](../cases/laravel/STOCK_003/plan.md), [STOCK_003](../cases/rails/STOCK_003/plan.md), [STOCK_004](../cases/laravel/STOCK_004/plan.md), [STOCK_004](../cases/rails/STOCK_004/plan.md), [STOCK_005](../cases/laravel/STOCK_005/plan.md), [STOCK_005](../cases/rails/STOCK_005/plan.md), [STOCK_006](../cases/laravel/STOCK_006/plan.md), [STOCK_006](../cases/rails/STOCK_006/plan.md), [STOCK_007](../cases/laravel/STOCK_007/plan.md), [STOCK_007](../cases/rails/STOCK_007/plan.md), [STOCK_008](../cases/laravel/STOCK_008/plan.md), [STOCK_008](../cases/rails/STOCK_008/plan.md), [TIME_001](../cases/laravel/TIME_001/plan.md), [TIME_001](../cases/rails/TIME_001/plan.md), [TIME_002](../cases/laravel/TIME_002/plan.md), [TIME_002](../cases/rails/TIME_002/plan.md), [TIME_003](../cases/laravel/TIME_003/plan.md), [TIME_003](../cases/rails/TIME_003/plan.md), [TIME_004](../cases/laravel/TIME_004/plan.md), [TIME_004](../cases/rails/TIME_004/plan.md), [TIME_005](../cases/laravel/TIME_005/plan.md), [TIME_005](../cases/rails/TIME_005/plan.md), [TIME_006](../cases/laravel/TIME_006/plan.md), [TIME_006](../cases/rails/TIME_006/plan.md), [TIME_007](../cases/rails/TIME_007/plan.md), [TIME_008](../cases/rails/TIME_008/plan.md)
