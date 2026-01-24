# AI Code Review Benchmark: Rails × Context Engineering Edition

**テーマ:** 仕様（Plan）と実装（Code）の整合性を検証する、Rails特化型AIレビューベンチマーク

**作成日:** 2025-01-24
**ステータス:** 計画確定

---

## 1. 検証の目的

### 1.1 Primary Goal
**DeepSeekはClaude Sonnetの代替になり得るか？**

APIコストが1/20のDeepSeek V3/R1が、実務レベルのコードレビュー品質を出せるかを定量的に検証する。

### 1.2 Secondary Goals

1. **Context Engineeringの実用性検証**
    - 単なるバグ探しではなく、「Plan（設計意図）通りに実装されているか」という高度なレビューが可能かを検証
    - PlanStackアプローチの有効性を実証

2. **Railsの「暗黙知」理解度の測定**
    - Convention over Configurationの文脈理解
    - 既存コードベース（Scope、メソッド）の活用判断
    - Rails Wayからの逸脱検知

---

## 2. 比較対象モデル

| モデル名 | コスト ($/1M input) | 役割・仮説 |
|----------|---------------------|------------|
| **Claude 3.5 Sonnet** | $3.00 | **Baseline（王者）** - 現在のPlanStack採用モデル。論理的整合性チェックで最も信頼性が高い |
| **DeepSeek V3** | $0.14 | **Cost Killer** - Sonnet比1/20のコスト。精度9割あれば実務のメインストリームになり得る |
| **DeepSeek R1** | $0.14 | **Reasoner（思考型）** - CoT（思考連鎖）により、複雑な仕様矛盾や副作用を見抜けるか |
| **Gemini 1.5 Pro** | $1.25 | **Long Context** - Plan抽出をサボり、リポジトリ全ファイルを読ませた場合の比較用 |

---

## 3. テストケース設計

### 3.1 概要

- **テーマ:** ECサイトの注文処理（Checkout）
- **総ケース数:** 60
- **フレームワーク:** Ruby on Rails のみ

### 3.2 カテゴリ構成

| カテゴリ | ケース数 | 検証ポイント | 期待する検知 |
|----------|----------|--------------|--------------|
| **Plan不整合** | 20 | 仕様通りに実装されていない（コードは動く） | 仕様との乖離を指摘 |
| **論理バグ** | 20 | N+1、トランザクション、セキュリティ | バグを指摘 |
| **False Positive** | 20 | 完璧なコード | 「LGTM」と言える（過剰検知しない） |

### 3.3 Plan不整合ケース（20件）

| # | バグ内容 | Planの指示 | 実装の誤り |
|---|----------|------------|------------|
| 01 | 割引率の誤記 | 「会員は10%割引」 | 0.1ではなく0.01を適用 |
| 02 | Scope無視 | 「active_ordersスコープを使用」 | `where(status: 'active')`を再実装 |
| 03 | 順序違反 | 「在庫確認→決済→メール送信の順」 | メール送信が決済前に実行 |
| 04 | 既存メソッド無視 | 「User#full_nameを使用」 | `"#{first_name} #{last_name}"`を再実装 |
| 05 | 境界値ミス | 「送料無料は5000円以上」 | 5000円「超」で判定 |
| 06 | enum不使用 | 「Order.statusesのenumを使用」 | 文字列リテラルで比較 |
| 07 | 関連の誤り | 「has_many :items経由で取得」 | 別クエリで取得 |
| 08 | コールバック重複 | 「after_createで通知」 | after_saveで実装（更新時も発火） |
| 09 | 時刻処理 | 「JSTで日付判定」 | UTCで判定 |
| 10 | 金額計算 | 「税込価格で計算」 | 税抜で計算 |
| 11 | 定数未使用 | 「Settings.tax_rateを使用」 | マジックナンバー直書き |
| 12 | バリデーション漏れ | 「数量は1-99の範囲」 | 上限チェックなし |
| 13 | ステータス遷移 | 「pending→confirmed→shippedの順」 | pending→shippedを許可 |
| 14 | 通知条件 | 「初回購入時のみウェルカムメール」 | 毎回送信 |
| 15 | 丸め処理 | 「小数点以下切り捨て」 | 四捨五入で実装 |
| 16 | キャッシュキー | 「user_idを含めること」 | order_idのみ |
| 17 | ログ出力 | 「個人情報はマスク」 | メールアドレスそのまま出力 |
| 18 | リトライ設計 | 「最大3回リトライ」 | 5回でハードコード |
| 19 | 排他制御 | 「楽観的ロックを使用」 | ロックなし |
| 20 | 外部キー | 「dependent: :destroyを設定」 | 設定なし |

### 3.4 論理バグケース（20件）

| # | バグ種別 | 内容 |
|---|----------|------|
| 01 | N+1 | includes漏れ（Order → Items） |
| 02 | N+1 | preload vs eager_load の誤用 |
| 03 | N+1 | ループ内でのcount呼び出し |
| 04 | トランザクション | 外部API呼び出しがトランザクション内 |
| 05 | トランザクション | ネストしたトランザクションのrequires_new漏れ |
| 06 | トランザクション | after_commit外でのジョブenqueue |
| 07 | Race Condition | 在庫デクリメントがアトミックでない |
| 08 | Race Condition | find_or_create_byの競合 |
| 09 | Race Condition | カウンターキャッシュの手動更新 |
| 10 | セキュリティ | Strong Parametersの漏れ |
| 11 | セキュリティ | 認可チェック漏れ（他人の注文参照可能） |
| 12 | セキュリティ | SQLインジェクション（where直書き） |
| 13 | メモリ | find_eachを使わず全件ロード |
| 14 | メモリ | pluckすべきところでselect |
| 15 | 例外処理 | rescueが広すぎて握りつぶし |
| 16 | 例外処理 | raise後のensureで例外上書き |
| 17 | 型エラー | nil安全でないメソッドチェーン |
| 18 | 型エラー | to_iのサイレント変換（"abc".to_i → 0） |
| 19 | 時刻バグ | TimeとDateTimeの混在 |
| 20 | 時刻バグ | サマータイム未考慮 |

### 3.5 False Positiveケース（20件）

バグのない完璧なコード。過剰検知率を測定するため、意図的に「紛らわしいが正しい」実装を含める。

| # | 内容 | 紛らわしいポイント |
|---|------|-------------------|
| 01-05 | 標準的な実装 | 特になし（ベースライン） |
| 06-10 | 複雑だが正しい | ネストしたトランザクション、複数のコールバック |
| 11-15 | 非典型だが正しい | Rails Wayと異なるが意図的な設計 |
| 16-20 | 高度な最適化 | 一見バグに見えるが正しいパフォーマンス最適化 |

---

## 4. 技術アーキテクチャ

### 4.1 リポジトリ構成

```
ai-review-benchmark/
├── cases/
│   └── rails/
│       ├── plan_mismatch/           # Plan不整合（20ケース）
│       │   ├── 01_discount_rate/
│       │   │   ├── plan.md          # 仕様書
│       │   │   ├── context.md       # 既存コードベースの情報
│       │   │   ├── impl.rb          # レビュー対象コード
│       │   │   └── meta.json        # 正解データ・解説
│       │   ├── 02_scope_ignored/
│       │   └── ...
│       ├── logic_bug/               # 論理バグ（20ケース）
│       │   └── ...
│       └── false_positive/          # 完璧なコード（20ケース）
│           └── ...
├── results/
│   └── {timestamp}_run/
│       ├── claude_sonnet.json
│       ├── deepseek_v3.json
│       ├── deepseek_r1.json
│       ├── gemini_pro.json
│       └── report.md                # 自動生成レポート
├── scripts/
│   ├── generator.py                 # テストケース生成
│   ├── runner.py                    # ベンチマーク実行
│   └── evaluator.py                 # 採点（LLM-as-a-Judge）
└── README.md
```

### 4.2 ケースファイル仕様

#### plan.md
```markdown
# 注文確定処理

## 要件
- 会員は10%割引を適用する
- 割引後の金額で決済処理を行う

## 使用すべき既存実装
- `User#member?` で会員判定
- `Order#apply_discount(rate)` で割引適用
```

#### context.md
```markdown
# 既存コードベース情報

## User モデル
- `member?`: 有料会員かどうかを返す
- `full_name`: 氏名を返す

## Order モデル
- `apply_discount(rate)`: 割引率を適用
- `scope :active_orders`: status が active のもの
```

#### impl.rb
```ruby
# レビュー対象コード
class CheckoutService
  def execute(order)
    if order.user.member?
      order.total *= 0.01  # バグ: 0.9 であるべき
    end
    PaymentGateway.charge(order.total)
  end
end
```

#### meta.json
```json
{
  "case_id": "plan_mismatch_01",
  "category": "plan_mismatch",
  "difficulty": "easy",
  "expected_detection": true,
  "bug_description": "割引率が10%ではなく99%になっている",
  "bug_location": "impl.rb:5",
  "correct_implementation": "order.total *= 0.9",
  "tags": ["calculation", "discount"],
  "notes": "数値の誤りは発見しやすいはず"
}
```

### 4.3 評価パイプライン

```
[Test Case] → [Target Model] → [Review Output] → [Judge Model] → [Score]
                                                      ↓
                                              Claude 3.5 Sonnet
                                              (+ GPT-4o for validation)
```

#### Judge の評価基準

| 指標 | 説明 | 値 |
|------|------|---|
| `detected` | 正解バグを指摘できたか | true/false |
| `accuracy` | 指摘内容の正確性 | 0-100 |
| `noise_count` | 無関係な指摘の数 | 整数 |
| `severity_match` | 重要度の判定が適切か | true/false |

### 4.4 集計指標

| 指標 | 計算方法 | 目標値 |
|------|----------|--------|
| **Recall** | 検知数 / 総バグ数 | > 80% |
| **Precision** | 正しい指摘 / 全指摘 | > 70% |
| **False Positive Rate** | 誤検知数 / FPケース数 | < 20% |
| **Cost per Review** | API費用 / ケース数 | 比較用 |
| **Latency** | 平均応答時間 | 参考値 |

---

## 5. 実行計画

### 5.1 Phase 1: 準備（2日）

- [ ] リポジトリ初期化
- [ ] ケース生成スクリプト作成
- [ ] 20ケース分のテストデータ作成（各カテゴリから数件ずつ）
- [ ] Judgeプロンプトの検証

### 5.2 Phase 2: パイロット（1日）

- [ ] Claude Sonnetで20ケース実行
- [ ] Judge精度の検証（人間採点との一致率）
- [ ] 必要に応じてプロンプト調整

### 5.3 Phase 3: 本番実行（2日）

- [ ] 残り40ケースの生成
- [ ] 全モデルで60ケース実行
- [ ] 結果集計・分析

### 5.4 Phase 4: 執筆（2日）

- [ ] Zenn記事執筆
- [ ] グラフ・図表作成
- [ ] レビュー・公開

---

## 6. アウトプット

### 6.1 Zenn記事構成案

**タイトル:**
「RailsのAIコードレビュー、Claude vs DeepSeek徹底比較 ── 60ケースで検証した"暗黙知"の理解力」

**構成:**

1. **Introduction**
    - コードレビュー自動化の壁は「仕様理解」にある
    - Context Engineering（PlanStackアプローチ）の解説

2. **Methodology**
    - 60ケース、4モデル
    - JSONによる定量評価の理由

3. **Results**
    - 精度比較（カテゴリ別）
    - コスト試算（月額いくらになるか）
    - 特筆すべき検知例・見逃し例

4. **Discussion**
    - DeepSeek V3は実用レベルか？
    - R1の思考連鎖は効果があったか？
    - Planの有無による差（あれば）

5. **Conclusion**
    - 推奨モデルと使い分け
    - PlanStack（Context Engineering）の重要性

### 6.2 今後の展開（別記事）

- **第2弾:** Next.jsでの検証（型があればPlanは不要か？）
- **第3弾:** FW横断比較（Rails vs Next.js vs Go）

---

## 7. リスクと対策

| リスク | 影響 | 対策 |
|--------|------|------|
| Judge精度が低い | 結果の信頼性低下 | パイロットで人間採点と比較、複数Judgeで検証 |
| DeepSeek APIの不安定 | 実行遅延 | リトライ機構、代替モデル準備 |
| ケース生成の偏り | 結果の一般性低下 | 複数人でケースレビュー |
| 想定外の結果 | 記事の方向性変更 | 結論先取りせず、事実ベースで執筆 |

---

## 8. 参考情報

### 8.1 先行研究

| 名称 | 概要 | 本検証との差異 |
|------|------|---------------|
| SWE-bench | GitHubのIssueからバグ修正を評価 | 生成タスク（レビューではない） |
| CodeReviewer (MS) | レビューコメント生成 | 仕様書との突き合わせではない |
| BigCodeBench | 実務的コーディングタスク | 生成タスク（レビューではない） |

### 8.2 関連リンク

- [PlanStack](https://plan-stack.ai)
- [DeepSeek API](https://platform.deepseek.com/)
- [Anthropic API](https://docs.anthropic.com/)

---

**Document Version:** 1.0
**Last Updated:** 2025-01-24