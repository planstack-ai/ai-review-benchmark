# Spring Boot (Kotlin) サポート追加計画

## 概要

AI Review Benchmark プロジェクトに Spring Boot (Kotlin) のサポートを追加する。既存の Java サポートを拡張し、Kotlin らしい実装でテストケースを作成する。

## 現状

| フレームワーク | ケース数 | パターンファイル | 状態 |
|---------------|---------|-----------------|------|
| Rails | 99 | patterns.yaml | 稼働中 |
| Django | 30 | patterns_django.yaml | 稼働中 |
| Laravel | 60 | (手動作成) | 稼働中 |
| Spring Boot (Java) | 33 | patterns_springboot.yaml | 稼働中 |
| **Spring Boot (Kotlin)** | **0** | **-** | **追加予定** |

## 決定事項

- **ディレクトリ**: `cases/springboot-kotlin/`（Java とは別ディレクトリ）
- **スコープ**: MVP 30 ケース（Django と同規模）
- **パターンファイル**: `patterns_springboot_kotlin.yaml`

---

## 実装計画

### フェーズ 1: インフラ整備

#### 1.1 ディレクトリ構造の作成

```
cases/springboot-kotlin/
├── CALC_001/
│   ├── meta.json
│   ├── plan.md
│   ├── context.md
│   └── impl.kt
├── CALC_002/
└── ...
```

#### 1.2 パターン定義ファイルの作成

`patterns_springboot_kotlin.yaml` を作成（MVP 30 パターン）:

| カテゴリ | 軸 | ケース数 |
|---------|-----|---------|
| CALC (6) | spec_alignment | 割引、税金、浮動小数点、丸め、ハードコード税率、送料境界 |
| AUTH (4) | spec_alignment | IDOR、カート操作、PreAuthorize、管理者権限 |
| STATE (4) | spec_alignment | 無効な遷移、競合状態、check-then-act、enum比較 |
| TIME (3) | spec_alignment | タイムゾーン、日付境界、キャンペーン期間 |
| STOCK (2) | spec_alignment | 競合状態、マイナス在庫検証 |
| NOTIFY (1) | spec_alignment | 非同期エラーハンドリング |
| SPRING (5) | implicit_knowledge | @Transactional、@EnableAsync、コンストラクタインジェクション、@Valid、例外処理 |
| FP (5) | false_positive | 正しく実装されたコード |

**合計: 30 ケース（25 バグ + 5 偽陽性）**

#### 1.3 runner.py の更新

`springboot-kotlin` を FRAMEWORK_CONFIG に追加:

```python
FRAMEWORK_CONFIG = {
    # ... 既存フレームワーク ...
    "springboot-kotlin": {
        "impl_ext": ".kt",
        "language": "Kotlin",
        "code_block": "kotlin",
    },
}
```

型定義の更新:

```python
FrameworkName = Literal["rails", "django", "laravel", "springboot", "springboot-kotlin"]
```

Kotlin 用のレビュープロンプトテンプレートを追加。

#### 1.4 evaluator.py の更新

フレームワーク選択肢に `springboot-kotlin` を追加。

#### 1.5 generator.py の更新

`springboot-kotlin` フレームワークオプションと Kotlin テンプレートのサポートを追加。

---

### フェーズ 2: テストケース作成

#### 2.1 Kotlin イディオマティックパターン

Java 実装との主な違い:

| Java | Kotlin |
|------|--------|
| `BigDecimal.valueOf(0.1)` | `BigDecimal("0.1")` または `0.1.toBigDecimal()` |
| `Optional<T>` | Nullable 型 `T?` |
| `@Autowired` フィールドインジェクション | コンストラクタインジェクション（デフォルト） |
| Getter/Setter | `data class` とプロパティ |
| `stream().map()...` | コレクション拡張関数 `.map {}` |
| `if (obj != null)` | `obj?.let {}` または `obj ?: default` |

#### 2.2 作成するケースカテゴリ

**Spec Alignment（20 ケース）:**

1. CALC_001: discount_rate_direction（割引率の方向ミス）
2. CALC_002: tax_calculation_order（税計算順序）
3. CALC_003: floating_point_currency（浮動小数点通貨）
4. CALC_004: inconsistent_rounding（不整合な丸め）
5. CALC_005: hardcoded_tax_rate（ハードコード税率）
6. CALC_006: free_shipping_boundary（送料無料境界）
7. AUTH_001: access_other_user_order（他ユーザー注文アクセス）
8. AUTH_002: manipulate_other_cart（他カート操作）
9. AUTH_003: preauthorize_condition_wrong（PreAuthorize条件ミス）
10. AUTH_004: admin_permission_missing（管理者権限欠落）
11. STATE_001: invalid_state_transition（無効な状態遷移）
12. STATE_002: state_update_conflict（状態更新競合）
13. STATE_003: check_then_act_race（check-then-act競合）
14. STATE_004: enum_comparison_wrong（enum比較ミス）
15. TIME_001: timezone_not_considered（タイムゾーン未考慮）
16. TIME_002: date_boundary_calculation（日付境界計算）
17. TIME_003: campaign_period_check（キャンペーン期間チェック）
18. STOCK_001: stock_race_condition（在庫競合状態）
19. STOCK_002: negative_stock_validation（マイナス在庫検証）
20. NOTIFY_001: async_notification_error（非同期通知エラー）

**Implicit Knowledge（5 ケース）:**

21. SPRING_001: transactional_propagation（トランザクション伝播）
22. SPRING_002: enable_async_missing（@EnableAsync欠落）
23. SPRING_003: field_injection_antipattern（フィールドインジェクション）
24. SPRING_004: valid_annotation_missing（@Valid欠落）
25. SPRING_005: exception_handling_wrong（例外処理ミス）

**False Positive（5 ケース）:**

26. FP_001: correct_discount_calculation（正しい割引計算）
27. FP_002: correct_tax_calculation（正しい税計算）
28. FP_003: correct_state_transition（正しい状態遷移）
29. FP_004: correct_timezone_handling（正しいタイムゾーン処理）
30. FP_005: correct_transactional_usage（正しいトランザクション使用）

#### 2.3 Kotlin 用 meta.json スキーマ

```json
{
  "case_id": "CALC_001",
  "category": "calculation",
  "axis": "spec_alignment",
  "name": "discount_rate_direction",
  "difficulty": "easy",
  "expected_detection": true,
  "bug_description": "Discount rate direction wrong, becomes 90% off",
  "bug_anchor": "total.multiply(BigDecimal(\"0.1\"))",
  "correct_implementation": "total.multiply(BigDecimal(\"0.9\"))",
  "severity": "critical",
  "tags": ["calculation", "discount", "member"],
  "framework": "springboot-kotlin",
  "framework_version": "3.2+",
  "kotlin_version": "1.9+"
}
```

---

### フェーズ 3: ドキュメント更新

#### 3.1 CLAUDE.md の更新

Kotlin コマンド例とテストケース数を追加。

#### 3.2 docs/benchmark-spec-v3.md の更新

Spring Boot (Kotlin) セクションを追加。

#### 3.3 case-catalog.md の更新

Kotlin テストケースエントリを追加。

---

## 実行順序

1. `patterns_springboot_kotlin.yaml` を作成
2. `runner.py` に Kotlin フレームワークサポートを追加
3. `evaluator.py` に Kotlin フレームワークサポートを追加
4. `cases/springboot-kotlin/` ディレクトリ構造を作成
5. 30 テストケースを作成（impl.kt, plan.md, context.md, meta.json）
6. `python scripts/runner.py --framework springboot-kotlin --model claude-sonnet` で検証
7. ドキュメントを更新

---

## Kotlin 実装例

**CALC_001 impl.kt（バグあり）:**

```kotlin
package com.example.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import com.example.model.Order
import com.example.model.Customer
import com.example.repository.OrderRepository
import com.example.repository.CustomerRepository
import java.math.BigDecimal
import java.math.RoundingMode
import java.time.LocalDateTime

@Service
@Transactional
class OrderDiscountService(
    private val orderRepository: OrderRepository,
    private val customerRepository: CustomerRepository
) {
    companion object {
        private val MEMBER_DISCOUNT_RATE = BigDecimal("0.1")
        private val MINIMUM_ORDER_AMOUNT = BigDecimal("50.00")
    }

    fun calculateFinalAmount(orderId: Long): BigDecimal {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found") }

        val baseAmount = order.totalAmount
        val customer = order.customer

        return if (isEligibleForDiscount(customer, baseAmount)) {
            applyMemberDiscount(baseAmount)
        } else {
            baseAmount
        }
    }

    private fun isEligibleForDiscount(customer: Customer?, orderAmount: BigDecimal): Boolean {
        return customer != null &&
               customer.isMembershipActive &&
               orderAmount >= MINIMUM_ORDER_AMOUNT
    }

    // BUG: 0.9 を掛けるべきところを 0.1 を掛けている
    private fun applyMemberDiscount(total: BigDecimal): BigDecimal {
        val discountAmount = total.multiply(MEMBER_DISCOUNT_RATE)
        return total.subtract(discountAmount).setScale(2, RoundingMode.HALF_UP)
    }
}
```

---

## 完了条件

- [ ] 30 Kotlin テストケースを作成
- [ ] `runner.py --framework springboot-kotlin` が動作する
- [ ] `evaluator.py` が Kotlin 結果を正しくスコアリングする
- [ ] すべての `meta.json` で `bug_anchor_verified: true`
- [ ] ドキュメント更新完了
