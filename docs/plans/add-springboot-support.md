# Spring Boot（Java/Kotlin）サポート追加計画

## 概要

AI Review Benchmark プロジェクトに Spring Boot フレームワークのサポートを追加し、Java/Kotlin の Spring Boot アプリケーションにおける AI コードレビュー品質を評価できるようにする。

## 現状

| フレームワーク | ケース数 | パターンファイル | 状態 |
|---------------|---------|-----------------|------|
| Rails | 99 | patterns.yaml | 稼働中 |
| Django | 30 | patterns_django.yaml | 稼働中 |
| Laravel | 60 | (手動作成) | 稼働中 |
| **Spring Boot** | **0** | **-** | **追加予定** |

---

## 実装計画

### フェーズ 1: インフラ整備

#### 1.1 ディレクトリ構造の作成

```
cases/springboot/
├── CALC_001/
│   ├── meta.json
│   ├── plan.md
│   ├── context.md
│   └── impl.java
├── CALC_002/
└── ...
```

#### 1.2 パターン定義ファイルの作成

`patterns_springboot.yaml` を作成：

```yaml
# AI Code Review Benchmark - Spring Boot Bug Pattern Definitions
# 30 MVP patterns for Spring Boot e-commerce order processing

- id: CALC_001
  category: calculation
  axis: spec_alignment
  name: discount_rate_direction
  plan: "Apply 10% discount for members"
  bug_description: "Discount rate direction wrong, becomes 90% off"
  correct: "total.multiply(BigDecimal.valueOf(0.9))"
  incorrect: "total.multiply(BigDecimal.valueOf(0.1))"
  severity: critical
  difficulty: easy
  tags: [calculation, discount, member]

- id: CALC_002
  category: calculation
  axis: spec_alignment
  name: tax_calculation_order
  plan: "Calculate total with 10% tax after discount"
  bug_description: "Tax calculation order wrong"
  correct: "subtotal.subtract(discount).multiply(BigDecimal.valueOf(1.1))"
  incorrect: "subtotal.multiply(BigDecimal.valueOf(1.1)).subtract(discount)"
  severity: high
  difficulty: medium
  tags: [calculation, tax, discount]
# ... 以下省略
```

#### 1.3 runner.py の更新

**FRAMEWORK_CONFIG への追加:**
```python
"springboot": {
    "impl_ext": ".java",
    "language": "Java",
    "code_block": "java",
},
```

**型定義の更新:**
```python
FrameworkName = Literal["rails", "django", "laravel", "springboot"]
```

**レビュープロンプトテンプレートの追加:**
```python
REVIEW_PROMPT_SPRINGBOOT_TEMPLATE = """You are a Senior Spring Boot Developer.
Review the following Java code against the specification.

## Specification (Plan)
{plan}

## Existing Codebase Context
{context}

## Code Under Review
```java
{impl}
```

## Output Format
Respond with ONLY the following JSON format (no other text):
```json
{{
  "has_issues": true/false,
  "issues": [
    {{
      "severity": "critical/major/minor",
      "type": "plan_mismatch/logic_bug/security/performance",
      "location": "line number or code location",
      "description": "description of the issue",
      "suggestion": "suggested fix"
    }}
  ],
  "summary": "overall findings"
}}
```

If there are no issues, set has_issues to false and issues to an empty array.
"""
```

**build_prompt() 関数の更新:**
```python
def build_prompt(case: dict, framework: str = "rails") -> str:
    # ... 既存コード ...
    elif framework == "springboot":
        template = REVIEW_PROMPT_SPRINGBOOT_TEMPLATE
```

**CLI 引数の更新:**
```python
parser.add_argument(
    "--framework",
    type=str,
    default="rails",
    choices=["rails", "django", "laravel", "springboot"],
    help="Framework to evaluate",
)
```

#### 1.4 evaluator.py の更新

**CLI 引数の更新:**
```python
parser.add_argument(
    "--framework",
    type=str,
    default="rails",
    choices=["rails", "django", "laravel", "springboot"],
)
```

#### 1.5 generator.py の更新

**FRAMEWORK_CONFIG への追加:**
```python
"springboot": {
    "impl_ext": ".java",
    "language": "Java",
    "expert_role": "Senior Spring Boot Developer",
    "orm": "Spring Data JPA",
    "patterns_file": "patterns_springboot.yaml",
},
```

**コード生成プロンプトの追加:**
```python
IMPL_PROMPT_SPRINGBOOT = """You are a Senior Spring Boot Developer.
Generate a Java implementation file with a bug based on the following specification.

Framework: Spring Boot 3.2+
Java Version: 21+
Build Tool: Gradle or Maven

Requirements:
1. Use Spring annotations (@Service, @Repository, @Transactional, etc.)
2. Use BigDecimal for monetary calculations
3. Follow Java naming conventions
4. Include proper imports
...
"""
```

---

### フェーズ 2: テストケース設計

#### 2.1 MVP ケース数目標

| 軸 | カテゴリ | ケース数 |
|---|---------|---------|
| 仕様合致 (Spec Alignment) | CALC, AUTH, STATE, TIME, STOCK, NOTIFY | 20 |
| 暗黙知識 (Implicit Knowledge) | SPRING | 8 |
| 偽陽性 (False Positive) | FP | 5 |
| **合計** | | **33** |

#### 2.2 Spring Boot 固有パターン（SPRING カテゴリ）

| ID | パターン | バグタイプ | 難易度 |
|----|---------|----------|-------|
| SPRING_001 | @Transactional の欠落/誤った伝播設定 | データ整合性 | medium |
| SPRING_002 | @EnableAsync なしで @Async を使用 | サイレント失敗 | hard |
| SPRING_003 | フィールドインジェクション vs コンストラクタインジェクション | テスト困難 | medium |
| SPRING_004 | リクエストボディに @Valid がない | バリデーションバイパス | easy |
| SPRING_005 | @ControllerAdvice での不適切な例外処理 | エラー情報漏洩 | medium |
| SPRING_006 | 循環依存の問題 | ランタイム障害 | hard |
| SPRING_007 | JPA リレーションでの N+1 クエリ | パフォーマンス | medium |
| SPRING_008 | @Cacheable のキー設定漏れ | キャッシュミス | medium |

#### 2.3 Spec Alignment パターン（既存カテゴリの移植）

**CALC (価格計算) - 6ケース:**
| ID | パターン |
|----|---------|
| CALC_001 | 割引率の方向誤り |
| CALC_002 | 税計算の順序誤り |
| CALC_003 | 浮動小数点精度エラー (BigDecimal) |
| CALC_004 | 一貫しない丸め処理 |
| CALC_005 | ハードコードされた税率 |
| CALC_006 | 送料無料の境界条件エラー |

**AUTH (認可) - 4ケース:**
| ID | パターン |
|----|---------|
| AUTH_001 | 所有者チェック漏れ |
| AUTH_002 | ロールチェック漏れ |
| AUTH_003 | @PreAuthorize の条件誤り |
| AUTH_004 | セッション検証の欠落 |

**STATE (状態遷移) - 4ケース:**
| ID | パターン |
|----|---------|
| STATE_001 | 無効な状態遷移の許可 |
| STATE_002 | 状態更新の競合 |
| STATE_003 | 状態チェックと更新の間の競合 |
| STATE_004 | enum 状態の不正な比較 |

**TIME (時間関連) - 3ケース:**
| ID | パターン |
|----|---------|
| TIME_001 | タイムゾーンの考慮漏れ |
| TIME_002 | 日付境界の処理誤り |
| TIME_003 | キャンペーン期間の判定誤り |

**STOCK (在庫) - 2ケース:**
| ID | パターン |
|----|---------|
| STOCK_001 | 在庫確認と予約の間の競合 |
| STOCK_002 | 在庫数の負数許可 |

**NOTIFY (通知) - 1ケース:**
| ID | パターン |
|----|---------|
| NOTIFY_001 | 非同期通知の失敗ハンドリング漏れ |

#### 2.4 False Positive パターン (FP) - 5ケース

| ID | 説明 |
|----|------|
| FP_001 | 正しい割引計算（指摘なしが正解） |
| FP_002 | 正しい @Transactional 使用 |
| FP_003 | 正しい認可チェック |
| FP_004 | 正しい状態遷移制御 |
| FP_005 | 正しい BigDecimal 計算 |

#### 2.5 meta.json スキーマ

```json
{
  "case_id": "SPRING_001",
  "category": "spring",
  "axis": "implicit_knowledge",
  "name": "missing_transactional_propagation",
  "difficulty": "medium",
  "expected_detection": true,
  "bug_description": "@Transactional missing proper propagation setting",
  "bug_anchor": "@Transactional",
  "correct_implementation": "@Transactional(propagation = Propagation.REQUIRED)",
  "severity": "high",
  "tags": ["spring", "transaction", "data-integrity"],
  "framework": "springboot",
  "framework_version": "3.2+",
  "java_version": "21+"
}
```

---

### フェーズ 3: 実装ファイルのサンプル

#### impl.java の例（CALC_001）

```java
package com.example.order.service;

import java.math.BigDecimal;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Order discount calculation service.
 */
@Service
public class MembershipDiscountService {

    private static final BigDecimal MEMBER_DISCOUNT_RATE = new BigDecimal("0.10");

    private BigDecimal subtotal;

    public MembershipDiscountService(BigDecimal subtotal) {
        this.subtotal = subtotal;
    }

    /**
     * Apply member discount to the subtotal.
     * Spec: 10% discount for members (pay 90% of original price)
     *
     * @return discounted total
     */
    @Transactional(readOnly = true)
    public BigDecimal applyMemberDiscount() {
        // BUG: Returns 10% of subtotal instead of 90%
        return subtotal.multiply(MEMBER_DISCOUNT_RATE);
    }
}
```

#### impl.java の例（SPRING_001: @Transactional 問題）

```java
package com.example.order.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OrderService {

    private final OrderRepository orderRepository;
    private final PaymentService paymentService;

    public OrderService(OrderRepository orderRepository, PaymentService paymentService) {
        this.orderRepository = orderRepository;
        this.paymentService = paymentService;
    }

    /**
     * Process order with payment.
     * Spec: Order and payment must be atomic
     */
    @Transactional  // BUG: Missing propagation, paymentService has its own transaction
    public void processOrder(Order order) {
        orderRepository.save(order);
        paymentService.processPayment(order);  // This has @Transactional(propagation = REQUIRES_NEW)
        // If payment fails, order is already committed!
    }
}
```

---

### フェーズ 4: ドキュメント更新

#### 4.1 CLAUDE.md の更新

**サポートフレームワーク表への追加:**
```markdown
| Framework | Pattern File | Cases Dir | Implementation |
|-----------|--------------|-----------|----------------|
| Rails | patterns.yaml | cases/rails/ | impl.rb |
| Django | patterns_django.yaml | cases/django/ | impl.py |
| Laravel | - | cases/laravel/ | impl.php |
| Spring Boot | patterns_springboot.yaml | cases/springboot/ | impl.java |
```

**コマンド例の追加:**
```bash
# Generate test case (Spring Boot)
python scripts/generator.py --framework springboot --pattern CALC_001

# Run benchmark (Spring Boot)
python scripts/runner.py --model claude-sonnet --framework springboot
```

#### 4.2 テストケース数の更新

```markdown
### Spring Boot (33 MVP)

| Axis | Categories | Cases |
|------|------------|-------|
| Spec Alignment | CALC, AUTH, STATE, TIME, STOCK, NOTIFY | 20 |
| Implicit Knowledge | SPRING | 8 |
| False Positive | FP | 5 |
```

---

## 変更対象ファイル一覧

| ファイル | 変更種別 | 説明 |
|---------|---------|------|
| `patterns_springboot.yaml` | 新規 | 33パターンの定義 |
| `cases/springboot/` | 新規 | テストケースディレクトリ |
| `scripts/runner.py` | 修正 | フレームワーク設定、プロンプト追加 |
| `scripts/evaluator.py` | 修正 | CLI 引数追加 |
| `scripts/generator.py` | 修正 | フレームワーク設定、生成ロジック追加 |
| `CLAUDE.md` | 修正 | ドキュメント更新 |

---

## 決定事項

| 項目 | 決定 | 理由 |
|-----|------|------|
| **言語** | Java のみ | ユーザーベースが広い、Spring Boot 公式サンプルが Java 中心。Kotlin は後から追加可能 |
| **Spring Boot** | 3.2+ | 最新 LTS、Java 21 サポート、AOT コンパイル対応 |
| **Java** | 21 (LTS) | 最新 LTS、レコード・パターンマッチング等の新機能 |
| **ビルドツール** | 言及のみ | コードは単一ファイルで完結。Gradle/Maven 設定は context.md で参照情報として提供 |

---

## 実装順序

1. ✅ 計画の承認を得る
2. `patterns_springboot.yaml` を作成（33パターン）
3. `scripts/runner.py` を更新
4. `scripts/evaluator.py` を更新
5. `scripts/generator.py` を更新
6. `cases/springboot/` ディレクトリを作成
7. テストケースを生成（`python scripts/generator.py --all --framework springboot`）
8. ベンチマークを実行して検証
9. `CLAUDE.md` を更新

---

## 作業見積もり

| タスク | 内容 |
|-------|------|
| patterns_springboot.yaml | 33パターンの YAML 定義 |
| runner.py 更新 | 設定 + プロンプト追加（約50行） |
| evaluator.py 更新 | CLI 引数追加（約5行） |
| generator.py 更新 | 設定 + プロンプト追加（約100行） |
| テストケース生成 | LLM による 33ケース生成 |
| 検証 | ベンチマーク実行・結果確認 |
