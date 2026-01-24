# CLAUDE.md - AI Review Benchmark Project Guide

## プロジェクト概要

RailsアプリケーションのAIコードレビュー品質を評価するベンチマークプロジェクト。
「Plan（仕様）とCode（実装）の整合性」を検証することで、Context Engineeringの有効性を実証する。

### Primary Goal

**DeepSeekはClaude Sonnetの代替になり得るか？**
APIコストが1/20のDeepSeek V3/R1が、実務レベルのコードレビュー品質を出せるかを定量的に検証。

### 比較対象モデル

| モデル | コスト ($/1M input) | 役割 |
|--------|---------------------|------|
| Claude 3.5 Sonnet | $3.00 | Baseline |
| DeepSeek V3 | $0.14 | Cost Killer |
| DeepSeek R1 | $0.14 | Reasoner |
| Gemini 1.5 Pro | $1.25 | Long Context |

## テストケース構成（計60ケース）

| カテゴリ | ケース数 | 検証ポイント |
|----------|----------|--------------|
| **plan_mismatch** | 20 | 仕様通りに実装されていない（コードは動く） |
| **logic_bug** | 20 | N+1、トランザクション、セキュリティ等 |
| **false_positive** | 20 | 完璧なコード（過剰検知しないか） |

## 評価指標

| 指標 | 計算方法 | 目標値 |
|------|----------|--------|
| **Recall** | 検知数 / 総バグ数 | > 80% |
| **Precision** | 正しい指摘 / 全指摘 | > 70% |
| **False Positive Rate** | 誤検知数 / FPケース数 | < 20% |
| **Cost per Review** | API費用 / ケース数 | 比較用 |

## コーディング規約

### Python（スクリプト）

- Python 3.11+
- 型ヒント必須
- フォーマッタ: black
- リンター: ruff
- docstring: Google style

### Ruby（テストケース）

- Ruby 3.2+ / Rails 7.1+
- 標準的なRails規約に従う
- rubocop準拠

## ディレクトリ構造

```
cases/rails/{category}/{case_id}/
├── plan.md      # 仕様書
├── context.md   # 既存コードベース情報
├── impl.rb      # レビュー対象コード
└── meta.json    # 正解データ
```

## テストケース作成ガイドライン

### plan.md

- 実装者が参照すべき要件を明記
- 「使用すべき既存実装」セクションで既存メソッド/スコープを指定
- 曖昧さを排除し、検証可能な形で記述

### context.md

- 既存のモデル、メソッド、スコープの情報
- レビュアー（AI）が参照できる「コードベースの知識」
- 実際のRailsプロジェクトを想定した構成

### impl.rb

- レビュー対象のコード（Service, Controller, Model等）
- plan.mdの要件に対する実装
- バグありケースは1-2個の問題を含める

### meta.json

```json
{
  "case_id": "plan_mismatch_01",
  "category": "plan_mismatch | logic_bug | false_positive",
  "difficulty": "easy | medium | hard",
  "expected_detection": true | false,
  "bug_description": "問題の説明",
  "bug_location": "impl.rb:行番号",
  "correct_implementation": "正しい実装例",
  "tags": ["calculation", "discount"],
  "notes": "補足情報"
}
```

## 実行コマンド

### テストケース生成
```bash
python scripts/generator.py --category plan_mismatch --count 20
```

### ベンチマーク実行
```bash
python scripts/runner.py --model claude-sonnet --cases cases/rails/
```

### 採点
```bash
python scripts/evaluator.py --run-dir results/2025xxxx_run/
```

## API設定

環境変数で各モデルのAPIキーを設定：

```bash
export ANTHROPIC_API_KEY=xxx
export DEEPSEEK_API_KEY=xxx
export GOOGLE_API_KEY=xxx
```

## 重要な設計判断

1. **Judgeモデル**: Claude 3.5 Sonnetを使用（+ GPT-4oでクロスバリデーション）
2. **評価形式**: JSON出力による定量評価（自然言語の曖昧さを排除）
3. **ケース独立性**: 各ケースは独立して評価可能な形で設計

## 注意事項

- テストケースは実在のRailsコードではなく、ベンチマーク用に作成したもの
- バグは意図的に埋め込んだもので、実際のセキュリティ脆弱性ではない
- 結果は各モデルの特定時点でのスナップショットであり、モデル更新により変動する可能性あり
