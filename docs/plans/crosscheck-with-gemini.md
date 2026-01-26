# Cross-Check Test Cases with gemini-3-pro

## Overview
Systematically review test cases to identify false positive inducing code, using gemini-3-pro for cross-validation.

---

## Progress Tracker

### Django (30 cases)
| Category | Cases | Status | Notes |
|----------|-------|--------|-------|
| FP_001-005 | 5 | ✅ DONE | Fixed all 5 cases, committed 0c052e8 |
| CALC_001-010 | 10 | ⏳ Pending | |
| AUTH_001-007 | 7 | ⏳ Pending | |
| DJANGO_001-008 | 8 | ⏳ Pending | |

### Rails (99 cases)
| Category | Cases | Status | Notes |
|----------|-------|--------|-------|
| FP_001-018 | 13 | 🔄 Partial | Fixed 9 cases, FPR 84.6%→69.2% |
| CALC_001-011 | 11 | ✅ Passed | All detected |
| AUTH_001-008 | 8 | ✅ Passed | All detected |
| TIME_001-008 | 8 | ⏳ Pending | API quota hit |
| STOCK_001-008 | 8 | ⏳ Pending | API quota hit |
| STATE_001-007 | 7 | ⏳ Pending | API quota hit |
| NOTIFY_001-006 | 6 | ✅ Passed | All detected |
| PERF_001-008 | 8 | ⏳ Pending | API quota hit |
| DATA_001-007 | 7 | ✅ Passed | All detected |
| EXT_001-007 | 7 | ✅ Passed | All detected |
| RAILS_001-016 | 16 | ⏳ Pending | API quota hit |

---

## Current Task: Rails All Cases (99 cases)

### Step 1: Run gemini-3-pro
```bash
source .venv/bin/activate
python scripts/runner.py --model gemini-3-pro --framework rails --output-dir results/crosscheck_rails/
```
- Estimated cost: ~$1.00
- Estimated time: ~60 minutes

### Step 2: Evaluate Results
```bash
python scripts/evaluator.py --run-dir results/crosscheck_rails/ --framework rails --skip-judge
```

### Step 3: Analyze Discrepancies
Priority order:
1. **FP cases** (FP_001-013) - Check if "clean" code has actual bugs
2. **Bug cases missed** - Check if bug_anchor is correct
3. **Severity mismatches** - Review meta.json

### Step 4: Fix Issues
For each discrepancy:
- Review `impl.rb` against `plan.md`
- Fix `impl.rb` if code has actual bugs
- Update `meta.json` if expected_detection is wrong
- Update `plan.md` or `context.md` if ambiguous

### Step 5: Re-run & Commit
- Re-run verification to confirm fixes
- Commit with descriptive message

---

## Commands Reference

```bash
# Run cross-check
python scripts/runner.py --model gemini-3-pro --framework {rails|django} --output-dir results/crosscheck_{framework}/

# Evaluate results
python scripts/evaluator.py --run-dir results/crosscheck_{framework}/ --framework {framework} --skip-judge

# Check specific case results
python -c "
import json
with open('results/crosscheck_{framework}/gemini-3-pro.json') as f:
    data = json.load(f)
for r in data:
    if r['case_id'] == 'FP_001':
        print(json.dumps(r['parsed_response'], indent=2))
"
```

---

## Completed Work

### 2026-01-26: Django FP Cases
- **Commit**: 0c052e8
- **Fixed**:
  - FP_001: CodeReviewService → Task Management System
  - FP_002: CodeReviewBenchmarkService → UserProfile
  - FP_003: CodeReviewBenchmarkService → UserActivityService
  - FP_004: Simplified analytics, aligned plan.md
  - FP_005: Fixed select_for_update bug, uniform price API
- **Result**: FPR reduced from 100% to ~0%

### 2026-01-26: Rails FP Cases
- **Status**: In Progress (API quota exceeded during verification)
- **Fixed** (9 cases):
  - FP_001: Schema alignment (name vs first_name/last_name, removed invalid columns)
  - FP_002: Removed password/confirmed_at, matched context schema
  - FP_003: CodeReviewBenchmarkService → UserProfileService
  - FP_004: UserAnalyticsService → UserActivityService
  - FP_005: Fixed callback logic bug (payment_method check)
  - FP_006: Schema alignment (removed undefined references)
  - FP_008: State machine alignment (matched context schema)
  - FP_011: CodeReviewBenchmarkService → AdminBypassService
  - FP_018: Removed undefined model references
- **Results**: FPR reduced from 84.6% (11/13) to 69.2% (9/13)
- **Remaining issues**: FP cases still fail due to plan.md/impl.rb spec mismatches
  - Gemini correctly identifies these as "plan_mismatch" issues
  - Further fixes would require updating plan.md to match simpler implementations