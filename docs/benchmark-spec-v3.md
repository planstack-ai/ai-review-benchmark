# AI Code Review Benchmark: Rails × Context Engineering Edition v3

**Theme:** A Rails-specific AI review benchmark to verify alignment between specifications (Plan) and implementation (Code)

**Created:** 2025-01-24
**Status:** Confirmed
**Version:** 3.0

---

## 1. Objectives

### 1.1 Primary Goal
**Can DeepSeek replace Claude Sonnet?**

Quantitatively verify whether DeepSeek V3/R1, at 1/20th the API cost, can deliver production-quality code review.

### 1.2 Secondary Goals

1. **Validate Context Engineering in Practice**
   - Test whether AI can perform advanced review checking "Is this implemented according to the Plan (design intent)?" rather than just bug hunting
   - Demonstrate the effectiveness of the PlanStack approach

2. **Measure Understanding of Rails "Implicit Knowledge"**
   - Understanding of Convention over Configuration context
   - Judgment on utilizing existing codebase (Scopes, methods)
   - Detection of deviations from the Rails Way

3. **Pioneer Framework App Development Benchmarks**
   - Existing benchmarks (HumanEval, SWE-bench) target competitive programming / OSS libraries
   - No benchmark exists for "building apps with frameworks" — the development pattern covering 90% of real-world work
   - Establish a pioneering example to fill this gap

---

## 2. Models Under Comparison

| Model | Cost ($/1M input) | Role & Hypothesis |
|-------|-------------------|-------------------|
| **Claude 3.5 Sonnet** | $3.00 | **Baseline (Champion)** - Current PlanStack model. Highest reliability for logical consistency checks |
| **DeepSeek V3** | $0.14 | **Cost Killer** - 1/20th the cost of Sonnet. Could become mainstream if accuracy reaches 90% |
| **DeepSeek R1** | $0.14 | **Reasoner (Thinking Model)** - Can CoT (Chain of Thought) detect complex spec contradictions and side effects? |
| **Gemini 1.5 Pro** | $1.25 | **Long Context** - Comparison when skipping Plan extraction and feeding entire repository files |

---

## 3. Test Case Design

### 3.1 Overview

- **Theme:** E-commerce order processing
- **Bug Patterns:** 75
- **False Positive Cases:** 20
- **Total Cases:** 95
- **Framework:** Ruby on Rails only
- **Generation Method:** AI auto-generation + human sample verification (20 cases)

### 3.2 Category Composition

| Category | Cases | Classification | Verification Points |
|----------|-------|----------------|---------------------|
| Price Calculation | 10 | Spec Alignment | Discounts, tax, rounding, currency |
| Inventory & Quantity | 8 | Spec Alignment | Stock allocation, race conditions, quantity validation |
| State Transitions | 7 | Spec Alignment | Order status, cancellation, refunds |
| User & Authorization | 7 | Spec Alignment | Permission checks, accessing other users' resources |
| Time & Duration | 8 | Spec Alignment | Timezone, period validation, boundary values |
| Notifications & Email | 6 | Spec Alignment | Duplicate sends, timing, recipients |
| External Integration | 6 | Implicit Knowledge | Payment API, Webhook, idempotency |
| Performance | 6 | Implicit Knowledge | N+1, full table loads, caching |
| Data Integrity | 6 | Implicit Knowledge | Constraints, locking, soft deletes |
| Rails-Specific | 11 | Implicit Knowledge | Scope, enum, callbacks, transactions |
| **False Positive** | 20 | - | No bugs. Can it say LGTM? |

### 3.3 Two-Axis Analysis

Results will be analyzed along two dimensions:

| Axis | Categories | What it measures |
|------|------------|------------------|
| **Spec Alignment** | CALC, STOCK, STATE, AUTH, TIME, NOTIFY | Can the model detect Plan vs Code mismatches? |
| **Implicit Knowledge** | PERF, DATA, RAILS, EXT | Can the model detect issues not written in Plan? |

---

## 4. Bug Pattern Details

### 4.1 Price Calculation (10 Patterns) — Spec Alignment

| # | ID | Pattern | Example |
|---|-----|---------|---------|
| 1 | CALC_001 | Discount rate direction error | `price * 0.1` (becomes 90% off) |
| 2 | CALC_002 | Tax calculation order | Discount→Tax vs Tax→Discount yields different amounts |
| 3 | CALC_003 | Inconsistent rounding | Round per item→sum vs sum→round |
| 4 | CALC_004 | Floating point currency | `0.1 + 0.2 != 0.3` problem |
| 5 | CALC_005 | Hardcoded tax rate | Still 8% instead of 10% |
| 6 | CALC_006 | Free shipping boundary | `>= 5000` vs `> 5000` |
| 7 | CALC_007 | Points calculation order | Applied before discount instead of after |
| 8 | CALC_008 | Coupon stacking logic | Allows duplicate application |
| 9 | CALC_009 | Minimum order amount check | Not considering post-discount amount |
| 10 | CALC_010 | Unit price × quantity overflow | Integer overflow on bulk orders |

### 4.2 Inventory & Quantity (8 Patterns) — Spec Alignment

| # | ID | Pattern | Example |
|---|-----|---------|---------|
| 11 | STOCK_001 | Stock allocation timing | Cart addition vs payment time |
| 12 | STOCK_002 | Non-atomic stock check and update | Race between `if stock > 0` and `stock -= 1` |
| 13 | STOCK_003 | Cart quantity vs stock divergence | Stock depleted while cart abandoned |
| 14 | STOCK_004 | Reserved vs actual stock confusion | Double-counting reserved stock |
| 15 | STOCK_005 | Zero quantity order allowed | Validation gap |
| 16 | STOCK_006 | Negative stock allowed | Cancellation processing goes negative |
| 17 | STOCK_007 | Duplicate stock restoration | Cancel spam increases stock |
| 18 | STOCK_008 | Bundle product stock calculation | Should take minimum of components |

### 4.3 State Transitions (7 Patterns) — Spec Alignment

| # | ID | Pattern | Example |
|---|-----|---------|---------|
| 19 | STATE_001 | Invalid state transition | Allows `shipped` → `pending` |
| 20 | STATE_002 | Cancel window check missing | Cancel succeeds after shipment |
| 21 | STATE_003 | Payment timeout | Payment allowed after expiration |
| 22 | STATE_004 | Duplicate payment | Double-click charges twice |
| 23 | STATE_005 | Partial cancel integrity | Total amount wrong after partial cancel |
| 24 | STATE_006 | Refund status update missing | Shows unpaid despite refund complete |
| 25 | STATE_007 | Delivery status regression | `delivered` → `shipping` |

### 4.4 User & Authorization (7 Patterns) — Spec Alignment

| # | ID | Pattern | Example |
|---|-----|---------|---------|
| 26 | AUTH_001 | Access other user's order | Just change ID in `/orders/123` |
| 27 | AUTH_002 | Manipulate other user's cart | Specify cart_id outside session |
| 28 | AUTH_003 | Deleted user's order display | Related data of deleted user |
| 29 | AUTH_004 | Admin permission check missing | Regular user can change prices |
| 30 | AUTH_005 | Guest gets member pricing | Hole in membership check logic |
| 31 | AUTH_006 | Access other user's points | Get other's points via API |
| 32 | AUTH_007 | Coupon owner check missing | Use other user's coupon code |

### 4.5 Time & Duration (8 Patterns) — Spec Alignment

| # | ID | Pattern | Example |
|---|-----|---------|---------|
| 33 | TIME_001 | Timezone not considered | Save UTC, display JST incorrectly |
| 34 | TIME_002 | Sale period boundary | 0:00 start becomes previous day 23:59 |
| 35 | TIME_003 | Coupon expiry comparison | `<` vs `<=` off by one day |
| 36 | TIME_004 | Date-only comparison error | Truncating time causes next-day treatment |
| 37 | TIME_005 | Month-end processing | 2/30 doesn't exist |
| 38 | TIME_006 | Year-crossing processing | 12/31 → 1/1 logic error |
| 39 | TIME_007 | Business day calculation | Not considering weekends/holidays |
| 40 | TIME_008 | Past delivery date allowed | Can specify yesterday |

### 4.6 Notifications & Email (6 Patterns) — Spec Alignment

| # | ID | Pattern | Example |
|---|-----|---------|---------|
| 41 | NOTIFY_001 | Duplicate email send | Retry sends 2 emails |
| 42 | NOTIFY_002 | Async error swallowed | Job fails but user not notified |
| 43 | NOTIFY_003 | Notification timing error | "Order complete" email before payment |
| 44 | NOTIFY_004 | Template variable error | `{{user.name}}` is nil |
| 45 | NOTIFY_005 | Recipient mixup | Email sent to wrong user |
| 46 | NOTIFY_006 | Bulk send rate limit | Mass send gets blocked |

### 4.7 External Integration (6 Patterns) — Implicit Knowledge

| # | ID | Pattern | Example |
|---|-----|---------|---------|
| 47 | EXT_001 | Payment API timeout unhandled | Charge success/failure unknown |
| 48 | EXT_002 | Webhook not idempotent | Same notification processed twice |
| 49 | EXT_003 | External API call inside transaction | Charge complete despite rollback |
| 50 | EXT_004 | Retry creates duplicate order | Network error → resend → 2 records |
| 51 | EXT_005 | Inventory sync delay | External warehouse diff not considered |
| 52 | EXT_006 | Shipping API error handling | Error swallowed, treated as success |

### 4.8 Performance (6 Patterns) — Implicit Knowledge

| # | ID | Pattern | Example |
|---|-----|---------|---------|
| 53 | PERF_001 | N+1 query | `order.items.each { \|i\| i.product.name }` |
| 54 | PERF_002 | Full table load | `Order.all.each` on 1M records |
| 55 | PERF_003 | Unnecessary eager loading | Loading unused associations |
| 56 | PERF_004 | Inefficient count query | `items.length` vs `items.count` |
| 57 | PERF_005 | Index not used | Search condition without index |
| 58 | PERF_006 | Cache key design error | Same cache key for all users |

### 4.9 Data Integrity (6 Patterns) — Implicit Knowledge

| # | ID | Pattern | Example |
|---|-----|---------|---------|
| 59 | DATA_001 | No foreign key constraint | Orphan records on parent delete |
| 60 | DATA_002 | Unique constraint missing | Multiple registrations with same email |
| 61 | DATA_003 | Optimistic locking not used | Concurrent edits overwrite |
| 62 | DATA_004 | Soft delete in search conditions | Deleted records in search results |
| 63 | DATA_005 | Master data history not kept | Product name change affects past orders |
| 64 | DATA_006 | Column addition default value | NULL causes downstream errors |

### 4.10 Rails-Specific Implicit Knowledge (11 Patterns) — Implicit Knowledge

| # | ID | Pattern | Example |
|---|-----|---------|---------|
| 65 | RAILS_001 | Scope not used, reimplemented | Writing `where(status: 'active')` every time |
| 66 | RAILS_002 | Enum not used | String literal comparison |
| 67 | RAILS_003 | Callback order dependency | `before_save` execution order changes result |
| 68 | RAILS_004 | `dependent: :destroy` missing | Children remain on parent delete |
| 69 | RAILS_005 | Job enqueue outside `after_commit` | Job runs despite rollback |
| 70 | RAILS_006 | Strong Parameters missing | Unintended column updates possible |
| 71 | RAILS_007 | `find_or_create_by` race | Duplicate records created |
| 72 | RAILS_008 | `update_all` skips callbacks | Validations also skipped |
| 73 | RAILS_009 | `pluck` vs `select` misuse | Unnecessary object instantiation |
| 74 | RAILS_010 | `includes` vs `preload` vs `eager_load` | Unintended query generated |
| 75 | RAILS_011 | `transaction` nesting | `requires_new: true` missing |

### 4.11 False Positive (20 Cases)

Bug-free, perfect code. Measures over-detection rate.

| # | Content | Misleading Points |
|---|---------|-------------------|
| FP_001-005 | Standard implementation | None (baseline) |
| FP_006-010 | Complex but correct | Nested transactions, multiple callbacks |
| FP_011-015 | Non-typical but correct | Intentional design differing from Rails Way |
| FP_016-020 | Advanced optimization | Correct performance optimization that looks like a bug |

---

## 5. Evaluation Design

### 5.1 Review Prompt (Plan Alignment Focus)

```
Review the following code against the Plan specification.

1. List the key requirements from the Plan
2. For each requirement, verify if the Code correctly implements it
3. Report any mismatches between Plan and Code
4. Report any bugs not related to Plan (logic errors, performance, security)
5. If everything is correct, respond with "LGTM"

Plan:
{plan.md}

Context (Existing Codebase):
{context.md}

Code to Review:
{impl.rb}
```

### 5.2 Scoring Rules

| Situation | Classification | Impact |
|-----------|----------------|--------|
| Correctly identifies the bug | True Positive (TP) | +1 to Recall |
| Correct bug + extra findings | TP + Noise | TP counted, noise tracked separately |
| Misses the bug | False Negative (FN) | -1 to Recall |
| Reports bug in bug-free code | False Positive (FP) | -1 to Precision |
| Improvement suggestion only (FP case) | OK | Not penalized |
| LGTM on bug-free code | OK | Correct behavior |
| Location info slightly off | Tolerated | TP if bug content matches |

### 5.3 Judge Configuration

| Item | Value |
|------|-------|
| Judge Model | Claude 3.5 Sonnet |
| Validation | 20 cases human-scored to verify Judge accuracy |
| Agreement Rate | Reported in results |
| Judge Prompt | Published in repository for reproducibility |
| Model Version | Recorded in results JSON |
| Execution Date | Recorded in results JSON |

### 5.4 Metrics

| Metric | Calculation | Target |
|--------|-------------|--------|
| **Recall** | TP / (TP + FN) | > 80% |
| **Precision** | TP / (TP + FP) | > 70% |
| **False Positive Rate** | FP cases flagged / 20 FP cases | < 20% |
| **Noise Rate** | Extra findings / Total findings | Reference |
| **Cost per Review** | API Cost / 95 cases | For comparison |
| **Latency** | Average response time | Reference |

### 5.5 Two-Axis Analysis

| Axis | Cases | Metrics |
|------|-------|---------|
| **Spec Alignment** | 46 (CALC, STOCK, STATE, AUTH, TIME, NOTIFY) | Recall, Precision |
| **Implicit Knowledge** | 29 (EXT, PERF, DATA, RAILS) | Recall, Precision |

---

## 6. Case File Specification

### 6.1 Directory Structure

```
ai-review-benchmark/
├── README.md
├── patterns.yaml
├── cases/
│   └── rails/
│       ├── CALC_001/
│       │   ├── plan.md
│       │   ├── context.md
│       │   ├── impl.rb
│       │   └── meta.json
│       ├── CALC_002/
│       └── ...
├── results/
│   └── 2025-01-xx/
│       ├── claude_sonnet.json
│       ├── deepseek_v3.json
│       ├── deepseek_r1.json
│       ├── gemini_pro.json
│       ├── judge_validation.json
│       └── report.md
├── scripts/
│   ├── generator.py
│   ├── runner.py
│   └── evaluator.py
├── prompts/
│   ├── review_prompt.md
│   └── judge_prompt.md
└── docs/
    └── benchmark-spec-v3.md
```

### 6.2 context.md Format (Real Code Snippets)

```markdown
# Existing Codebase

## Schema
```ruby
# orders table
# - id: bigint
# - user_id: bigint (foreign key)
# - status: integer (enum)
# - total: decimal(10,2)
# - created_at: datetime

# order_items table
# - id: bigint
# - order_id: bigint (foreign key)
# - product_id: bigint (foreign key)
# - quantity: integer
# - unit_price: decimal(10,2)
```

## User Model
```ruby
class User < ApplicationRecord
  has_many :orders

  def member?
    membership_status == 'active'
  end

  def full_name
    "#{first_name} #{last_name}"
  end
end
```

## Order Model
```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy

  enum status: { pending: 0, confirmed: 1, shipped: 2, delivered: 3, canceled: 4 }

  scope :active, -> { where.not(status: :canceled) }
  scope :recent, -> { where('created_at > ?', 30.days.ago) }

  def apply_discount(rate)
    self.total = total * (1 - rate)
  end
end
```
```

### 6.3 meta.json Format

```json
{
  "case_id": "CALC_001",
  "category": "calculation",
  "axis": "spec_alignment",
  "name": "discount_rate_direction",
  "difficulty": "easy",
  "expected_detection": true,
  "bug_description": "Discount rate direction wrong, becomes 90% off instead of 10% off",
  "bug_anchor": "total * 0.1",
  "correct_implementation": "total * 0.9",
  "severity": "critical",
  "tags": ["calculation", "discount", "member"]
}
```

### 6.4 Results JSON Format

```json
{
  "meta": {
    "benchmark_version": "3.0",
    "execution_date": "2025-01-25",
    "judge_model": "claude-3-5-sonnet-20241022",
    "temperature": 0
  },
  "models": {
    "claude_sonnet": {
      "model_id": "claude-3-5-sonnet-20241022",
      "total_cases": 95,
      "spec_alignment": {
        "cases": 46,
        "tp": 40,
        "fn": 6,
        "recall": 0.87
      },
      "implicit_knowledge": {
        "cases": 29,
        "tp": 22,
        "fn": 7,
        "recall": 0.76
      },
      "false_positive": {
        "cases": 20,
        "flagged": 3,
        "fp_rate": 0.15
      },
      "overall": {
        "recall": 0.83,
        "precision": 0.78,
        "noise_rate": 0.12
      },
      "cost_usd": 2.85,
      "avg_latency_ms": 3200
    }
  }
}
```

---

## 7. Execution Plan

### 7.1 Phase 1: Preparation (2 days)

- [ ] Initialize repository (PlanStack workspace)
- [ ] Create patterns.yaml (75 bug patterns + 20 FP)
- [ ] Create generation scripts
- [ ] Create review prompt and judge prompt
- [ ] Manually generate 10 cases to verify format

### 7.2 Phase 2: Case Generation (2 days)

- [ ] AI generates 95 cases
- [ ] Human reviews 20 cases (check for "AI smell", realistic Rails code)
- [ ] Adjust prompts and regenerate as needed

### 7.3 Phase 3: Pilot (1 day)

- [ ] Run 20 cases with Claude Sonnet
- [ ] Human scores same 20 cases
- [ ] Calculate Judge-Human agreement rate
- [ ] Adjust Judge prompt if agreement < 80%

### 7.4 Phase 4: Production Run (2 days)

- [ ] Run all 95 cases with all 4 models (temperature=0)
- [ ] Aggregate and analyze results
- [ ] Compare accuracy by category and axis

### 7.5 Phase 5: Writing (2 days)

- [ ] Write Zenn article
- [ ] Create graphs and charts (overall + two-axis breakdown)
- [ ] Review and publish

---

## 8. Deliverables

### 8.1 Zenn Article Structure

**Title:**
"Rails AI Code Review: Claude vs DeepSeek Showdown — Detection Power Tested on 95 Real-World Bug Cases"

**Structure:**

1. **Introduction**
   - Why are AI benchmarks mostly "competitive programming"?
   - The missing evaluation criteria for FW app development (90% of real work)
   - Static tools (RuboCop, Brakeman) cannot detect Plan alignment issues
   - "Plan creation → Code generation → Review" all by AI, humans just decide

2. **Methodology**
   - 75 bug patterns + 20 FP cases = 95 total
   - Two-axis evaluation: Spec Alignment vs Implicit Knowledge
   - AI-driven test case auto-generation
   - LLM-as-a-Judge with human validation (20 cases, agreement rate reported)

3. **Results**
   - Overall accuracy comparison (Recall, Precision, FP Rate)
   - Spec Alignment axis breakdown
   - Implicit Knowledge axis breakdown
   - Cost estimation (monthly cost per model)
   - Notable detection examples and misses

4. **Discussion**
   - Is DeepSeek V3 production-ready?
   - Strengths and weaknesses by axis
   - Did R1's chain-of-thought help?
   - Limitations and future work

5. **Conclusion**
   - Recommended models and use cases
   - Importance of PlanStack (Context Engineering)
   - Future of FW app development benchmarks

### 8.2 Future Work (Separate Articles)

- **Part 2:** Next.js validation (Are types enough without Plans?)
- **Part 3:** Cross-FW comparison (Rails vs Next.js vs Laravel)
- **Part 4:** Collect PRs from Rails core/Devise OSS for additional cases

---

## 9. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Low quality generated cases | Reduced reliability | Human reviews 20 cases, check for "AI smell", regenerate as needed |
| Low Judge accuracy | Reduced reliability | Pilot with 20 human-scored cases, report agreement rate, adjust prompt if < 80% |
| Judge bias toward Claude | Credibility issue | Publish Judge prompt, report human agreement rate as validation |
| DeepSeek API instability | Execution delays | Retry mechanism, backup models |
| Unexpected results | Article direction change | Don't jump to conclusions, write based on facts |
| Pattern bias | Reduced generalizability | Distributed across 10 categories + 2 axes |
| Judge drift (model updates) | Reproducibility issue | Record judge model version and execution date in results |
| AI-generated bug bias | AI may find/miss AI-generated bugs differently | Note as limitation, human review for realism |
| FP "improvement suggestion" ambiguity | Scoring inconsistency | Clearly defined: bug report = FP, improvement suggestion = OK |
| Location drift | Evaluation breaks if line numbers change | Use bug_anchor (string match) instead of line numbers |

---

## 10. Disclaimers

- **Single execution:** All models run once with temperature=0. This measures tendency, not statistical significance.
- **Judge model:** Claude 3.5 Sonnet is used as Judge. Human validation on 20 cases provides baseline agreement rate.
- **AI-generated cases:** Test cases are AI-generated. 20 cases are human-reviewed for realism.
- **Rails-specific:** Results may not generalize to other frameworks.

---

## 11. References

### 11.1 Differences from Prior Work

| Name | Target | Task | Difference from This Study |
|------|--------|------|---------------------------|
| HumanEval | Algorithms | Generation | Competitive programming, divorced from practice |
| SWE-bench | OSS Libraries | Generation | Not FW apps |
| SWE-bench Multilingual | Same (multilingual) | Generation | No Rails |
| CodeReviewer | PR Comments | Review | Not spec alignment |
| **This Study** | **Rails Apps** | **Review** | **Plan vs Implementation Alignment** |

### 11.2 Related Links

- [PlanStack](https://plan-stack.ai)
- [DeepSeek API](https://platform.deepseek.com/)
- [Anthropic API](https://docs.anthropic.com/)
- [SWE-bench](https://www.swebench.com/)

---

## Appendix: Case Summary

### By Category

| Category | Cases | Axis |
|----------|-------|------|
| CALC (Price Calculation) | 10 | Spec Alignment |
| STOCK (Inventory) | 8 | Spec Alignment |
| STATE (State Transitions) | 7 | Spec Alignment |
| AUTH (Authorization) | 7 | Spec Alignment |
| TIME (Time & Duration) | 8 | Spec Alignment |
| NOTIFY (Notifications) | 6 | Spec Alignment |
| EXT (External Integration) | 6 | Implicit Knowledge |
| PERF (Performance) | 6 | Implicit Knowledge |
| DATA (Data Integrity) | 6 | Implicit Knowledge |
| RAILS (Rails-Specific) | 11 | Implicit Knowledge |
| FP (False Positive) | 20 | - |
| **Total** | **95** | |

### By Axis

| Axis | Categories | Cases |
|------|------------|-------|
| Spec Alignment | CALC, STOCK, STATE, AUTH, TIME, NOTIFY | 46 |
| Implicit Knowledge | EXT, PERF, DATA, RAILS | 29 |
| False Positive | FP | 20 |
| **Total** | | **95** |

---

**Document Version:** 3.0
**Last Updated:** 2025-01-24
