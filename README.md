# AI Code Review Benchmark: Rails × Context Engineering Edition

**テーマ:** 仕様（Plan）と実装（Code）の整合性を検証する、Rails特化型AIレビューベンチマーク

## 概要

このベンチマークは、LLMによるコードレビューの品質を定量的に評価するためのものです。
単なるバグ検出ではなく、**「Plan（設計意図）通りに実装されているか」** という高度なレビュー能力を測定します。

### Primary Goal

**DeepSeekはClaude Sonnetの代替になり得るか？**

APIコストが1/20のDeepSeek V3/R1が、実務レベルのコードレビュー品質を出せるかを定量的に検証します。

### 比較対象モデル

| モデル | コスト ($/1M input) | 役割 |
|--------|---------------------|------|
| Claude 3.5 Sonnet | $3.00 | Baseline |
| DeepSeek V3 | $0.14 | Cost Killer |
| DeepSeek R1 | $0.14 | Reasoner |
| Gemini 1.5 Pro | $1.25 | Long Context |

## ディレクトリ構成

```
ai-review-benchmark/
├── cases/
│   └── rails/
│       ├── plan_mismatch/     # Plan不整合（20ケース）
│       ├── logic_bug/         # 論理バグ（20ケース）
│       └── false_positive/    # 完璧なコード（20ケース）
├── results/                   # 実行結果
├── scripts/
│   ├── generator.py           # テストケース生成
│   ├── runner.py              # ベンチマーク実行
│   └── evaluator.py           # 採点（LLM-as-a-Judge）
├── CLAUDE.md                  # Claude Code用設定
└── README.md
```

## テストケース

### カテゴリ構成（計60ケース）

| カテゴリ | ケース数 | 検証ポイント |
|----------|----------|--------------|
| **Plan不整合** | 20 | 仕様通りに実装されていない（コードは動く） |
| **論理バグ** | 20 | N+1、トランザクション、セキュリティ |
| **False Positive** | 20 | 完璧なコード（過剰検知しないか） |

### ケースファイル構成

各ケースは以下の4ファイルで構成されます：

- `plan.md` - 仕様書（レビュー時に参照すべき要件）
- `context.md` - 既存コードベースの情報
- `impl.rb` - レビュー対象コード
- `meta.json` - 正解データ・メタ情報

## 使い方

### 1. 環境構築

```bash
pip install -r requirements.txt
```

### 2. テストケース生成

```bash
python scripts/generator.py
```

### 3. ベンチマーク実行

```bash
python scripts/runner.py --model claude-sonnet
python scripts/runner.py --model deepseek-v3
python scripts/runner.py --model deepseek-r1
python scripts/runner.py --model gemini-pro
```

### 4. 採点・レポート生成

```bash
python scripts/evaluator.py --run-dir results/{timestamp}_run
```

## 評価指標

| 指標 | 計算方法 | 目標値 |
|------|----------|--------|
| **Recall** | 検知数 / 総バグ数 | > 80% |
| **Precision** | 正しい指摘 / 全指摘 | > 70% |
| **False Positive Rate** | 誤検知数 / FPケース数 | < 20% |
| **Cost per Review** | API費用 / ケース数 | 比較用 |

## ライセンス

MIT License

## 関連リンク

- [PlanStack](https://plan-stack.ai)
