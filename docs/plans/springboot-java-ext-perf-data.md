# Plan: Add EXT, PERF, DATA Categories to Spring Boot Java

## Overview

Add 22 new test cases to Spring Boot Java covering:
- **EXT** (External Services): 7 cases
- **PERF** (Performance): 8 cases
- **DATA** (Data Integrity): 7 cases

## EXT Cases (External Services)

| Case ID | Name | Bug Description | Spring Boot Equivalent |
|---------|------|-----------------|------------------------|
| EXT_001 | payment_timeout_unhandled | Payment timeout leaves order in unknown state | RestTemplate/WebClient timeout not handled |
| EXT_002 | webhook_not_idempotent | Same webhook processed multiple times | Missing idempotency key check in @PostMapping |
| EXT_003 | api_call_in_transaction | Payment charged even if transaction rolls back | External API call inside @Transactional |
| EXT_004 | retry_duplicate_order | Network retry creates duplicate order records | Spring Retry without idempotency |
| EXT_005 | inventory_sync_delay | External warehouse stock diff not considered | Async inventory sync race condition |
| EXT_006 | shipping_error_swallowed | Shipping API error swallowed, treated as success | Empty catch block on RestClientException |
| EXT_007 | injection_vulnerabilities | Path traversal, XML injection vulnerabilities | Unsanitized input in file paths, XML processing |

## PERF Cases (Performance)

| Case ID | Name | Bug Description | Spring Boot Equivalent |
|---------|------|-----------------|------------------------|
| PERF_001 | n_plus_one_query | N+1 query on order items | Missing @EntityGraph or JOIN FETCH |
| PERF_002 | full_table_load | Loading all records into memory | findAll() on large table without pagination |
| PERF_003 | unnecessary_eager_loading | Eager loading unused associations | FetchType.EAGER on rarely-used relations |
| PERF_004 | inefficient_count | Loading records just to count | list.size() instead of repository.count() |
| PERF_005 | index_not_used | Search on non-indexed column | Query on non-indexed field |
| PERF_006 | cache_key_design | Cache key collision | @Cacheable with bad key design |
| PERF_007 | in_memory_aggregation | In-memory sort/aggregate large data | Stream operations on large findAll() |
| PERF_008 | n_plus_one_bulk_metrics | N+1 in bulk operation | Loop with individual queries |

## DATA Cases (Data Integrity)

| Case ID | Name | Bug Description | Spring Boot Equivalent |
|---------|------|-----------------|------------------------|
| DATA_001 | no_foreign_key | No FK constraint - orphan records | Missing @JoinColumn or cascade config |
| DATA_002 | unique_constraint_missing | Duplicate records allowed | Missing @UniqueConstraint |
| DATA_003 | optimistic_lock_missing | Last write wins silently | Missing @Version field |
| DATA_004 | soft_delete_in_query | Deleted records in results | Missing @Where(clause="deleted=false") |
| DATA_005 | master_data_history | Price change affects past orders | No snapshot of master data at order time |
| DATA_006 | column_default_null | NULL default causes errors | @Column without nullable=false or default |
| DATA_007 | batch_counting_inaccurate | Batch import wrong count | saveAll() count mismatch with unique constraints |

## Implementation Steps

1. Create directory structure for each case
2. Create plan.md based on Rails equivalent
3. Create context.md with Spring Boot specific context
4. Create impl.java with the bug
5. Create meta.json with proper metadata
6. Update patterns_springboot_java.yaml if needed

## File Structure

```
cases/springboot-java/
├── EXT_001/
│   ├── plan.md
│   ├── context.md
│   ├── impl.java
│   └── meta.json
├── EXT_002/
...
```

## Estimated New Total

- Current: 33 cases
- Adding: 22 cases
- New Total: 55 cases

## Priority Order

1. PERF (most common in real code reviews)
2. DATA (critical for data integrity)
3. EXT (external service issues)
