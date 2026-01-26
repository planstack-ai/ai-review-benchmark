# Test Cases

This directory contains test cases for the AI Code Review Benchmark.

## Overview

Test cases are organized into two main categories:

| Type | Description | `expected_detection` |
|------|-------------|----------------------|
| **Bug Cases** | Code with intentional bugs to detect | `true` |
| **Clean Cases (FP)** | Correct code to test for over-detection | `false` |

### Two-Axis Framework

Bug cases are analyzed along two dimensions:

```
Bug Cases                         Clean Cases
┌──────────────────────────┐     ┌─────────────┐
│ Spec Alignment           │     │    FP       │
│ CALC,STOCK,STATE,AUTH,   │     │             │
│ TIME,NOTIFY              │     │ Tests       │
├──────────────────────────┤     │ over-       │
│ Implicit Knowledge       │     │ detection   │
│ EXT,PERF,DATA,RAILS,     │     │             │
│ DJANGO                   │     │             │
└──────────────────────────┘     └─────────────┘
```

| Axis | What it measures | Categories |
|------|------------------|------------|
| **Spec Alignment** | Can AI detect Plan vs Code mismatches? | CALC, STOCK, STATE, AUTH, TIME, NOTIFY |
| **Implicit Knowledge** | Can AI detect issues not in Plan? | EXT, PERF, DATA, RAILS, DJANGO |

## File Structure

Each case contains 5 files. Read them in this order:

| # | File | Purpose |
|---|------|---------|
| 1 | `plan.md` | Specification document (requirements) |
| 2 | `context.md` | Existing codebase information |
| 3 | `impl.rb` / `impl.php` / `impl.py` | Code under review |
| 4 | `meta.json` | Ground truth and metadata |
| 5 | `expected_critique.md` | Expected review findings |

```
cases/
├── rails/
│   └── {CASE_ID}/
│       ├── plan.md              # What the code should do
│       ├── context.md           # Existing codebase context
│       ├── impl.rb              # Code to review
│       ├── meta.json            # Ground truth
│       └── expected_critique.md # Expected findings
├── laravel/
│   └── {CASE_ID}/
│       ├── plan.md
│       ├── context.md
│       ├── impl.php             # PHP implementation
│       ├── meta.json
│       └── expected_critique.md
└── django/
    └── {CASE_ID}/
        ├── plan.md
        ├── context.md
        ├── impl.py              # Python implementation
        ├── meta.json
        └── expected_critique.md
```

## Case Types

### Bug Cases (`expected_detection: true`)

Cases with intentional bugs. AI should detect and report them.

**meta.json fields:**
- `bug_description`: What the bug is
- `bug_anchor`: Code snippet containing the bug
- `correct_implementation`: How it should be fixed
- `severity`: `critical` | `high` | `medium` | `low`

### False Positive Cases (`expected_detection: false`)

Correct code that may look suspicious. AI should say "LGTM" or only suggest minor improvements.

**meta.json fields:**
- `bug_description`: `null`
- `bug_anchor`: `null`
- `severity`: `null`

## Evaluation Modes

Each case specifies its evaluation mode in `meta.json`:

| Mode | Description | Use Case |
|------|-------------|----------|
| `severity` | Keyword matching + severity scoring | Default, simple bugs |
| `semantic` | LLM judges against `expected_critique.md` | Complex or nuanced bugs |
| `dual` | Runs both explicit and implicit context | Implicit Knowledge cases |

## Naming Conventions

| Prefix | Category | Axis |
|--------|----------|------|
| `CALC` | Price Calculation | Spec Alignment |
| `STOCK` | Inventory & Quantity | Spec Alignment |
| `STATE` | State Transitions | Spec Alignment |
| `AUTH` | Authorization | Spec Alignment |
| `TIME` | Time & Duration | Spec Alignment |
| `NOTIFY` | Notifications | Spec Alignment |
| `EXT` | External Integration | Implicit Knowledge |
| `PERF` | Performance | Implicit Knowledge |
| `DATA` | Data Integrity | Implicit Knowledge |
| `RAILS` | Rails-Specific | Implicit Knowledge |
| `DJANGO` | Django-Specific | Implicit Knowledge |
| `FP` | False Positive | - |

## What Makes a Good Case

1. **One bug per case** - Each case tests exactly one issue
2. **Natural-looking code** - Bugs should be subtle, not obvious typos
3. **Verifiable requirements** - Clear spec in `plan.md` to check against
4. **Realistic context** - `context.md` provides enough codebase info
5. **Proper metadata** - Complete and accurate `meta.json`

## Framework Coverage

| Framework | Bug Cases | FP Cases | Total |
|-----------|-----------|----------|-------|
| Rails | 86 | 13 | 99 |
| Laravel | 50 | 10 | 60 |
| Django | 25 | 5 | 30 |
| **Total** | **161** | **28** | **189** |

## Quick Links

- [Case Catalog](../docs/case-catalog.md) - Complete list with links
- [Test Case Guide](../docs/testcase-guide.md) - How to create new cases
- [Benchmark Spec](../docs/benchmark-spec-v3.md) - Full specification
