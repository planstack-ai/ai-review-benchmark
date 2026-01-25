# README Improvement Plan

## Overview

READMEを「公開して読まれる」「突っ込まれても耐える」品質に改善する。

## Key Findings from Codebase

- **Temperature**: 未設定（モデルデフォルト使用、非決定的）
- **max_tokens**: 4096（全モデル共通）
- **Retry**: なし（単発実行）
- **FPR**: 2種類ある（Case-FPR と Finding-FPR）
- **Ensemble Judge**: Claude + Gemini実装済み

## Changes to Make

### 1. Add "Replacement Criteria" Section (HIGH)

**Location**: Primary Goal の直後

```markdown
### Replacement Criteria

For DeepSeek to be considered a viable replacement for Claude Sonnet:

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Recall | >= 80% | Must catch critical bugs |
| Case-FPR | <= 20% | Acceptable false alarm rate |
| Weighted Recall Gap | <= 10pp vs Sonnet | Similar severity assessment |
| Cost | <= 1/5 of Sonnet | Cost advantage requirement |

**Decision Matrix**:
- **Replace**: All thresholds met at 1/5th cost
- **Supplement**: Recall >= 70%, usable for first-pass review
- **Not Ready**: Any metric significantly below threshold
```

### 2. Fix Sample Output (HIGH)

**Location**: Example Results section

**Before**: FPR 100.0% (misleading)

**After**:
```markdown
> **Note**: Sample data for illustration. Run `python scripts/evaluator.py` for actual results.

| Model | Recall | Weighted Recall | Case-FPR | Cost |
|-------|--------|-----------------|----------|------|
| claude-sonnet | 85.2% | 72.4% | 15.0% | $2.85 |
| deepseek-v3 | 79.8% | 65.3% | 22.5% | $0.14 |
```

### 3. Add "Execution Settings" Section (HIGH)

**Location**: After Usage section

```markdown
## Execution Settings

| Setting | Value | Notes |
|---------|-------|-------|
| Temperature | Model default | Not explicitly set; uses provider defaults |
| max_tokens | 4096 | All models |
| Retry | None | Single attempt per case |
| Timeout | Provider default | SDK-dependent |

**Reproducibility Notes**:
- Results may vary slightly between runs due to non-zero temperature
- For deterministic results, modify `runner.py` to set `temperature=0`
```

### 4. Rewrite Evaluation Metrics (HIGH)

**Location**: Replace entire Evaluation Metrics section

```markdown
## Evaluation Metrics

### Detection Classifications

| Outcome | Definition |
|---------|------------|
| **True Positive (TP)** | Bug case where AI detected the bug |
| **False Negative (FN)** | Bug case where AI missed the bug |
| **True Negative (TN)** | FP case where AI correctly said LGTM |
| **False Positive (FP)** | FP case where AI incorrectly flagged critical bug |

### Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| **Recall** | TP / (TP + FN) | >= 80% |
| **Weighted Recall** | Sum(detection_score) / bug_cases | >= 70% |
| **Case-FPR** | FP / 20 FP cases | <= 20% |
| **Finding-FPR** | findings in FP cases / 20 | Reference |

**Detection Score by Severity**: critical=1.0, major=0.5, minor=0.2

> **Note**: All metrics are **macro averages** (averaged across cases).
```

### 5. Add Judge Bias Mitigation (MEDIUM)

**Location**: After Evaluation System section

```markdown
### Judge Bias Mitigation

To address "Claude judging Claude" bias concerns:

1. **Ensemble Mode**: Uses both Claude + Gemini as judges
   - Score: Mean of semantic scores
   - Detection: Majority vote

2. **Human Validation**: 20 cases validated against human judgment

3. **Transparency**: Judge prompts and model versions published in repository
```

### 6. Add Two-Axis Visual (MEDIUM)

**Location**: Two-Axis Analysis section

```
Bug Cases (79)                    Clean Cases (20)
┌──────────────────────┐         ┌─────────────┐
│ Spec Alignment (46)  │         │    FP (20)  │
│ CALC,STOCK,STATE,... │         │             │
├──────────────────────┤         │ Tests       │
│ Implicit Know. (33)  │         │ over-       │
│ EXT,PERF,DATA,RAILS  │         │ detection   │
└──────────────────────┘         └─────────────┘
    ↓ DETECTION                      ↓ RESTRAINT
```

### 7. Improve Cost Table (MEDIUM)

**Location**: Models Under Comparison

- Add Output cost column
- Add pricing date note: "*Pricing as of January 2025. Check provider docs for current rates.*"

### 8. Add "What Good Looks Like" Example (MEDIUM)

**Location**: After Example Results

Concise example using CALC_001:
- Bug code snippet (3 lines)
- Ideal JSON response
- Scoring explanation (1 line)

## Files to Modify

- `/Users/matsudashinsuke/Work/plan-stack/ai-review-benchmark/README.md`

## Verification

1. `git diff README.md` to review changes
2. Check markdown rendering (tables, code blocks)
3. Verify case count consistency (99 cases = 79 bug + 20 FP)