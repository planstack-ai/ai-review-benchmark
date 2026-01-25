# AI Review Benchmark 改善計画

## 概要

評価システムの4つの改善を実装する：
1. マルチJudgeアンサンブル（2-3モデル）
2. 構造化抽出による意味層評価
3. 要素ベースの期待値管理
4. 2段階FP/ノイズメトリクス

## 現状

- **Judge**: Claude Sonnet 4 単一モデル (`scripts/evaluator.py:33`)
- **FPR**: ケース単位（20件中何件でcritical検出したか）
- **期待値**: `expected_critique.md`（自由記述）+ `meta.json`（bug_anchor）
- **Noise Rate**: 追跡されているが体系的でない

---

## 実装計画

### Phase 1: マルチJudgeアンサンブル

**目的**: 複数モデルで判定し、mean_score + stddev で安定性を可視化

**採用モデル**: Claude + Gemini（2モデル構成）

**ファイル変更**:
- 新規: `scripts/judges/` ディレクトリ
  - `base.py` - 抽象Judgeクラス
  - `claude_judge.py` - Claude Sonnet Judge（既存ロジック抽出）
  - `gemini_judge.py` - Gemini Judge
  - `ensemble.py` - アンサンブル集計
- 修正: `scripts/evaluator.py` - ensemble対応

**CLI拡張**:
```bash
python scripts/evaluator.py --run-dir results/xxx/ \
    --judge-mode=ensemble \
    --judges=claude,gemini
```

**出力形式**:
```json
{
  "judge_scores": {
    "claude": {"semantic_score": 5, "detected": true},
    "gemini": {"semantic_score": 5, "detected": true}
  },
  "ensemble_score": {
    "mean": 5.0,
    "stddev": 0.0,
    "consensus": true
  }
}
```

**コスト見積**: 2-judge ensemble で約1.3倍（$0.012/case）

**実装状況**: ✅ 完了 (Sprint 1)

---

### Phase 2: 構造化抽出による意味層評価

**目的**: 文章比較ではなく「要素が揃っているか」で評価

**新規ファイル**:
- `scripts/extractors/finding_extractor.py` - 構造化抽出
- `scripts/extractors/element_matcher.py` - 要素照合

**抽出する要素**:
```python
@dataclass
class ExtractedFinding:
    category: str      # calculation_error, security, performance, etc.
    evidence: str      # コード引用
    impact: str        # 影響の説明
    severity: str      # critical, major, minor
    fix_proposal: str  # 修正案
```

**評価フロー**:
1. AIレビュー出力からLLMで構造化抽出
2. 期待要素（must_find）と照合
3. matched/missed 要素をスコア化

**実装状況**: ✅ 完了 (Sprint 2)

---

### Phase 3: 要素ベースの期待値管理

**目的**: 表現ではなく「必須要素の集合」で正解を定義

**meta.json スキーマ拡張**（後方互換）:
```json
{
  "case_id": "CALC_001",
  "expected_detection": true,
  "bug_anchor": "total * 0.1",

  "must_find": [
    {
      "id": "discount_inverted",
      "category": "calculation_error",
      "keywords": ["0.1", "90%", "discount", "inverted"],
      "severity_expected": "critical"
    }
  ]
}
```

**移行戦略**:
1. 既存フィールドは維持（後方互換）
2. `must_find` は optional で追加
3. 移行スクリプトで既存95件を段階的に変換

**実装状況**: ✅ 完了 (Sprint 3)

---

### Phase 4: 2段階FP/ノイズメトリクス

**目的**: ケース単位 + 指摘単位でFPを計測

**新規ファイル**: `scripts/metrics/fp_metrics.py`

**メトリクス定義**:

| メトリクス | 計算式 | 意味 |
|-----------|--------|------|
| Case-FPR | FPケースで誤検出した数 / 20 | 既存（維持） |
| Finding-FPR | FPケース内の誤指摘総数 / 20 | 新規：ノイズの量を計測 |
| TP-Noise-Rate | TPケース内のノイズ指摘 / 総指摘数 | 新規：正解時の過剰報告 |

**出力形式**:
```json
{
  "fp_metrics": {
    "case_fpr": 0.15,
    "finding_fpr": 0.35,
    "total_fp_findings": 7,
    "fp_breakdown": {"critical": 2, "major": 3, "minor": 2}
  },
  "tp_noise_metrics": {
    "total_findings_in_tp": 402,
    "noise_findings_in_tp": 89,
    "noise_rate_in_tp": 0.22
  }
}
```

**実装状況**: ✅ 完了 (Sprint 1)

---

## 実装順序

```
Phase 1 (Ensemble) ─────┬─────> Phase 2 (Extraction)
                        │              ↓
Phase 4 (FP Metrics) ───┘       Phase 3 (Elements)
```

**選択された順序**:
1. **Sprint 1**: Phase 1 (Ensemble) + Phase 4 (FP Metrics) を並行実装 ✅
2. **Sprint 2**: Phase 2 (Extraction)
3. **Sprint 3**: Phase 3 (Elements)

---

## 修正対象ファイル

| ファイル | 変更内容 | 状況 |
|---------|---------|------|
| `scripts/evaluator.py` | ensemble対応、新メトリクス統合 | ✅ |
| `scripts/runner.py` | CLI フラグ追加 | 🔲 |
| `cases/rails/*/meta.json` | must_find フィールド追加（段階的） | 🔲 |

## 新規作成ファイル

### Sprint 1（並行実装）✅
| ファイル | 目的 | 状況 |
|---------|------|------|
| `scripts/judges/base.py` | Judge抽象クラス | ✅ |
| `scripts/judges/claude_judge.py` | Claude Judge | ✅ |
| `scripts/judges/gemini_judge.py` | Gemini Judge | ✅ |
| `scripts/judges/ensemble.py` | アンサンブル集計 | ✅ |
| `scripts/metrics/fp_metrics.py` | FPメトリクス | ✅ |
| `scripts/config.py` | Judge設定の一元管理 | ✅ |

### Sprint 2（構造化抽出）✅
| ファイル | 目的 | 状況 |
|---------|------|------|
| `scripts/extractors/__init__.py` | Module exports | ✅ |
| `scripts/extractors/finding_extractor.py` | 構造化抽出 | ✅ |
| `scripts/extractors/element_matcher.py` | 要素照合 | ✅ |

### Sprint 3（要素ベース期待値）✅
| ファイル | 目的 | 状況 |
|---------|------|------|
| `scripts/migrate_must_find.py` | must_find追加移行 | ✅ |

---

## 検証方法

1. **ユニットテスト**: 各モジュールの単体テスト
2. **回帰テスト**: 既存結果との比較（`--judge-mode=single` で従来動作確認）
3. **コスト確認**: `--dry-run-cost` フラグで実行前にコスト見積
4. **パイロット実行**: 10件のケースで ensemble + 新メトリクス検証

---

## リスクと対策

| リスク | 対策 |
|-------|------|
| API コスト増加 | `--budget` フラグで上限設定、dry-run対応 |
| Judge間の不一致 | consensus_rate を追跡、低一致時はフラグ |
| 後方互換性 | 全新規フィールドはoptional、既存動作を保持 |
| 抽出のハルシネーション | カテゴリを許可リストで検証 |

---

## 実装履歴

### 2026-01-25: Sprint 1 完了

**Phase 1 (Multi-Judge Ensemble)**
- `scripts/config.py` - JudgeConfig dataclass, cost estimation
- `scripts/judges/` module with BaseJudge, ClaudeJudge, GeminiJudge, EnsembleJudge
- CLI: `--judge-mode`, `--judges`, `--dry-run-cost`, `--budget`

**Phase 4 (FP/Noise Metrics)**
- `scripts/metrics/fp_metrics.py` - FPMetrics, TPNoiseMetrics
- Case-FPR, Finding-FPR, TP-Noise-Rate calculations
- Integrated into `metrics.json` output

### 2026-01-25: Sprint 2 完了

**Phase 2 (Structured Extraction)**
- `scripts/extractors/finding_extractor.py`
  - `ExtractedFinding` dataclass with category normalization
  - `FindingExtractor` class with LLM-based and direct parsing
  - 21 valid categories (allowlist to prevent hallucination)
- `scripts/extractors/element_matcher.py`
  - `ExpectedElement` for must_find schema
  - `ElementMatcher` with weighted scoring (keyword 0.5, category 0.3, severity 0.2)
  - `match_findings()` convenience function
  - `evaluate_with_elements()` for full pipeline

### 2026-01-25: Sprint 3 完了

**Phase 3 (Element-Based Expectation Management)**
- `scripts/migrate_must_find.py`
  - Rule-based keyword extraction from bug_anchor, bug_description, expected_critique.md
  - Optional LLM-based generation with `--use-llm` flag
  - Category mapping to 21 valid extractor categories
  - Dry-run mode for preview
  - Category filter support

**Migration CLI:**
```bash
# Preview all changes
python scripts/migrate_must_find.py --all --dry-run

# Migrate specific case
python scripts/migrate_must_find.py --case CALC_001

# Migrate all with LLM (better quality)
python scripts/migrate_must_find.py --all --use-llm

# Migrate by category
python scripts/migrate_must_find.py --all --category calculation
```

**must_find Schema:**
```json
{
  "must_find": [
    {
      "id": "calc_001_main",
      "category": "calculation_error",
      "keywords": ["total", "0.1", "discount"],
      "severity_expected": "critical",
      "description": "Discount rate direction wrong",
      "required": true
    }
  ]
}
```
