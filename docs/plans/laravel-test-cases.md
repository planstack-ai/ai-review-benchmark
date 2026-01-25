# Laravel Test Cases Implementation Plan

## Overview

Create Laravel test cases following the existing Rails structure for the AI code review benchmark.

## Goals

1. Establish Laravel case directory structure under `cases/laravel/`
2. Create equivalent categories matching Rails distribution
3. Adapt meta.json schema for Laravel-specific patterns

## Proposed Structure

```
cases/laravel/{CASE_ID}/
├── plan.md              # Specification (requirements/constraints)
├── context.md           # Existing codebase (schema, models)
├── impl.php             # Code under review (with bug)
├── meta.json            # Evaluation metadata
├── expected_critique.md # Expected review content
├── context_base.md      # [LARAVEL cases only] Base code
└── context_guidelines.md # [LARAVEL cases only] Convention guidelines
```

## Category Distribution

| Axis | Categories | Target Count |
|------|------------|--------------|
| spec_alignment | CALC, STOCK, STATE, AUTH, TIME, NOTIFY | ~46 |
| implicit_knowledge | EXT, PERF, DATA, LARAVEL | ~33 |
| false_positive | FP | ~20 |

**Total target: ~99 cases** (matching Rails)

## Implementation Phases

### Batch 1: Foundation + Core Cases (30 cases)
- CALC_001-010 (10 cases) - Calculation bugs
- AUTH_001-007 (7 cases) - Authorization vulnerabilities
- STOCK_001-008 (8 cases) - Inventory management
- FP_001-005 (5 cases) - False positive tests

### Batch 2: State/Time/Notify (30 cases)
- STATE_001-007 (7 cases) - State machine issues
- TIME_001-008 (8 cases) - Timezone handling
- NOTIFY_001-006 (6 cases) - Notification issues
- FP_006-010 (5 cases) - False positive tests
- PERF_001-004 (4 cases) - Performance issues

### Batch 3: Implicit Knowledge + FP (39 cases)
- EXT_001-006 (6 cases) - External API issues
- PERF_005-006 (2 cases) - Performance issues
- DATA_001-006 (6 cases) - Data integrity
- LARAVEL_001-015 (15 cases) - Framework conventions
- FP_011-020 (10 cases) - False positive tests

## Laravel-Specific Adaptations

### Code Patterns
| Rails | Laravel |
|-------|---------|
| ActiveRecord | Eloquent ORM |
| `scope :active` | `scopeActive()` |
| Service Objects | Services/Actions |
| `before_action` | Middleware |
| `validates` | Form Requests / `$rules` |

### Bug Categories
- **LARAVEL_***: Eloquent misuse, middleware issues, service container problems
- **PERF_***: N+1 queries, missing eager loading, cache issues
- **DATA_***: Migration issues, foreign key constraints, soft deletes

### meta.json Adaptations
```json
{
  "case_id": "CALC_001",
  "category": "calculation",
  "axis": "spec_alignment",
  "framework": "laravel",
  "framework_version": "11.x",
  "php_version": "8.2+",
  ...
}
```

## Files to Update

1. `CLAUDE.md` - Add Laravel to supported frameworks
2. `scripts/runner.py` - Support `--cases cases/laravel/`
3. `scripts/evaluator.py` - Handle PHP file extensions
4. `docs/benchmark-spec-v3.md` - Document Laravel cases

## Success Criteria

- [ ] All 99 Laravel cases created
- [ ] Each case follows the established file structure
- [ ] meta.json validates against schema
- [ ] Scripts can run Laravel cases
- [ ] Evaluation metrics meet targets (Recall >80%, Precision >70%)

## Open Questions

1. Should we start with fewer cases (e.g., 20-30) as MVP?
2. Priority of categories - which to implement first?
3. Any Laravel-specific bug categories to add?