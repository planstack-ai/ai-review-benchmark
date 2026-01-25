# Evaluator Scoring Logic Bug Fixes

## Problem Summary

ユーザーの分析により、`evaluator.py` の評価JSON出力に以下の矛盾・バグが発見された：

1. `detected: true` なのに `detection_score: 0.0` になる場合がある
2. `highest_severity: null` なのに、レビューに severity が含まれている
3. `major_count: 0` 等の severity カウントが常に 0（semantic モード時）
4. `noise_count: 0` が常に 0（bug ケースの severity モード時）

## Root Cause Analysis

### 1. Semantic Mode での Severity 情報喪失 (Critical)

**File:** `scripts/evaluator.py` lines 560-562

```python
"critical_count": 0,    # ← ハードコード
"major_count": 0,       # ← ハードコード
"minor_count": 0,       # ← ハードコード
```

AI レビューアーの `parsed_response.issues` 配列には severity 情報があるが、
semantic 評価時に完全に無視されている。

### 2. highest_severity が常に None (Critical)

**File:** `scripts/evaluator.py` line 555

```python
"highest_severity": None,  # Not used in semantic evaluation
```

これにより metrics 計算（lines 780-782）で severity 別検出カウントが全て 0 になる。

### 3. Bug ケースで noise_count が常に 0 (High)

**File:** `scripts/evaluator.py` line 715

```python
noise_count = 0  # ノイズは無視（人間が判断するため）
```

severity モードで rubric 外の指摘をノイズとしてカウントしていない。

## Proposed Fixes

### Fix 1: Semantic Mode で Severity を抽出

`evaluate_with_semantic_judge()` 関数内で、`parsed_response` から severity カウントを抽出する。

**変更箇所:** lines 552-573

```python
# Add helper function or inline code to extract severity counts
issues = review_result.get("parsed_response", {}).get("issues", [])
critical_count = sum(1 for i in issues if i.get("severity", "").lower() == "critical")
major_count = sum(1 for i in issues if i.get("severity", "").lower() in ("major", "high"))
minor_count = sum(1 for i in issues if i.get("severity", "").lower() in ("minor", "low"))

# Set highest_severity based on counts
if critical_count > 0:
    highest_severity = "critical"
elif major_count > 0:
    highest_severity = "major"
elif minor_count > 0:
    highest_severity = "minor"
else:
    highest_severity = None
```

**Return dict の変更:**
- line 555: `"highest_severity": highest_severity,`
- lines 560-562: 実際のカウント値を使用

### Fix 2: Noise Count の計算（Issue数ベース）

**選択: Option A（シンプル・Issue数ベース）**
- Semantic モード: Judge の `noise_issues_count` を使用（現状維持）
- Severity モード: 期待される issue 数を超える分をノイズとしてカウント

line 715 を以下に変更：
```python
# Expected bug count from meta.json (default 1)
expected_bug_count = meta.get("expected_bug_count", 1)
total_issues = len(issues)
noise_count = max(0, total_issues - expected_bug_count)
```

### Fix 3: Severity Mode での Detection Score 整合性

現状の severity モードでは：
- critical → 1.0
- major → 0.5
- minor → 0.2
- none → 0.0

これは意図的な設計だが、`detected: true` と `detection_score` の関係を明確にする：

```python
# detection_score > 0 when detected == True
if detected:
    assert detection_score > 0, "detection_score should be > 0 when detected"
```

## Files to Modify

1. **`scripts/evaluator.py`**
   - `evaluate_with_semantic_judge()` (lines 490-595): severity 抽出ロジック追加
   - `evaluate_without_judge()` (lines 657-742): noise_count 計算修正

2. **`cases/rails/*/meta.json`** (optional)
   - `expected_bug_count` フィールド追加（デフォルト 1 なので既存ケースは変更不要）

## Verification

### Unit Test Scenarios

1. **Semantic mode with issues having severity**
   - Input: `parsed_response.issues` with mixed severities
   - Expected: `critical_count`, `major_count`, `minor_count` が正しく集計される
   - Expected: `highest_severity` が最高レベルに設定される

2. **Bug case with extra findings**
   - Input: 4 issues when only 1 bug expected
   - Expected: `noise_count = 3`

3. **Detection consistency**
   - Input: Any detected=true case
   - Expected: `detection_score > 0`

### Integration Test

```bash
# Run evaluator on RAILS_011 case
python scripts/evaluator.py --cases cases/rails/RAILS_011 --model gpt-4o

# Verify output
# - detected: true → detection_score > 0
# - issues count → severity counts match
# - noise_count reflects extra findings
```

## Impact Assessment

- **Breaking Change:** No（フィールド追加、既存フィールドの値修正のみ）
- **Metrics への影響:** あり
  - `critical_detections`, `major_detections`, `minor_detections` が正確になる
  - `noise_count` の総計が変わる
- **既存結果との比較:** 再評価が必要

## Implementation Order

1. Fix 1: Semantic mode severity extraction（最優先）
2. Fix 3: Detection score consistency check
3. Fix 2: Noise count calculation（Option A）

## Implementation Status

- [x] Fix 1: Semantic mode severity extraction - **DONE**
- [x] Fix 2: Noise count calculation - **DONE**
- [x] Fix 3: Detection score consistency - **Verified (already correct by design)**

## Verification Results

### Before (Bug Patterns Found)
```
ISSUE 3: AUTH_001 - semantic mode with all severity counts=0
ISSUE 4: AUTH_001 - bug case with noise_count=0 but 6 issues
```

### After (Fixed)
```
Model: deepseek-v3 - NO ISSUES FOUND
```

### Example: AUTH_001 Case
| Field | Before | After |
|-------|--------|-------|
| `highest_severity` | `None` | `critical` |
| `critical_count` | `0` | `1` |
| `major_count` | `0` | `2` |
| `minor_count` | `0` | `3` |
| `noise_count` | `0` | `5` (6 issues - 1 expected) |

### Metrics Summary
| Metric | Before | After |
|--------|--------|-------|
| `critical_detections` | `0` | `62` |
| `major_detections` | `0` | `12` |
| `total_noise` | `0` | `406` |
