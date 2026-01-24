# AI Code Review Benchmark: Rails × Context Engineering Edition v2

**Theme:** A Rails-specific AI review benchmark to verify alignment between specifications (Plan) and implementation (Code)

**Created:** 2025-01-24
**Status:** Confirmed
**Version:** 2.0

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
- **Total Patterns:** 75
- **Total Cases:** 100+ (1-2 cases per pattern)
- **Framework:** Ruby on Rails only
- **Generation Method:** AI auto-generation + human sample verification

### 3.2 Category Composition

| Category | Patterns | Verification Points |
|----------|----------|---------------------|
| Price Calculation | 10 | Discounts, tax, rounding, currency |
| Inventory & Quantity | 8 | Stock allocation, race conditions, quantity validation |
| State Transitions | 7 | Order status, cancellation, refunds |
| User & Authorization | 7 | Permission checks, accessing other users' resources |
| Time & Duration | 8 | Timezone, period validation, boundary values |
| External Integration | 6 | Payment API, Webhook, idempotency |
| Performance | 6 | N+1, full table loads, caching |
| Data Integrity | 6 | Constraints, locking, soft deletes |
| Notifications & Email | 6 | Duplicate sends, timing, recipients |
| Rails-Specific | 11 | Scope, enum, callbacks, transactions |
| **False Positive** | 20 | No bugs. Can it say LGTM? |

---

## 4. Bug Pattern Details

### 4.1 Price Calculation (10 Patterns)

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

### 4.2 Inventory & Quantity (8 Patterns)

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

### 4.3 State Transitions (7 Patterns)

| # | ID | Pattern | Example |
|---|-----|---------|---------|
| 19 | STATE_001 | Invalid state transition | Allows `shipped` → `pending` |
| 20 | STATE_002 | Cancel window check missing | Cancel succeeds after shipment |
| 21 | STATE_003 | Payment timeout | Payment allowed after expiration |
| 22 | STATE_004 | Duplicate payment | Double-click charges twice |
| 23 | STATE_005 | Partial cancel integrity | Total amount wrong after partial cancel |
| 24 | STATE_006 | Refund status update missing | Shows unpaid despite refund complete |
| 25 | STATE_007 | Delivery status regression | `delivered` → `shipping` |

### 4.4 User & Authorization (7 Patterns)

| # | ID | Pattern | Example |
|---|-----|---------|---------|
| 26 | AUTH_001 | Access other user's order | Just change ID in `/orders/123` |
| 27 | AUTH_002 | Manipulate other user's cart | Specify cart_id outside session |
| 28 | AUTH_003 | Deleted user's order display | Related data of deleted user |
| 29 | AUTH_004 | Admin permission check missing | Regular user can change prices |
| 30 | AUTH_005 | Guest gets member pricing | Hole in membership check logic |
| 31 | AUTH_006 | Access other user's points | Get other's points via API |
| 32 | AUTH_007 | Coupon owner check missing | Use other user's coupon code |

### 4.5 Time & Duration (8 Patterns)

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

### 4.6 External Integration (6 Patterns)

| # | ID | Pattern | Example |
|---|-----|---------|---------|
| 41 | EXT_001 | Payment API timeout unhandled | Charge success/failure unknown |
| 42 | EXT_002 | Webhook not idempotent | Same notification processed twice |
| 43 | EXT_003 | External API call inside transaction | Charge complete despite rollback |
| 44 | EXT_004 | Retry creates duplicate order | Network error → resend → 2 records |
| 45 | EXT_005 | Inventory sync delay | External warehouse diff not considered |
| 46 | EXT_006 | Shipping API error handling | Error swallowed, treated as success |

### 4.7 Performance (6 Patterns)

| # | ID | Pattern | Example |
|---|-----|---------|---------|
| 47 | PERF_001 | N+1 query | `order.items.each { \|i\| i.product.name }` |
| 48 | PERF_002 | Full table load | `Order.all.each` on 1M records |
| 49 | PERF_003 | Unnecessary eager loading | Loading unused associations |
| 50 | PERF_004 | Inefficient count query | `items.length` vs `items.count` |
| 51 | PERF_005 | Index not used | Search condition without index |
| 52 | PERF_006 | Cache key design error | Same cache key for all users |

### 4.8 Data Integrity (6 Patterns)

| # | ID | Pattern | Example |
|---|-----|---------|---------|
| 53 | DATA_001 | No foreign key constraint | Orphan records on parent delete |
| 54 | DATA_002 | Unique constraint missing | Multiple registrations with same email |
| 55 | DATA_003 | Optimistic locking not used | Concurrent edits overwrite |
| 56 | DATA_004 | Soft delete in search conditions | Deleted records in search results |
| 57 | DATA_005 | Master data history not kept | Product name change affects past orders |
| 58 | DATA_006 | Column addition default value | NULL causes downstream errors |

### 4.9 Notifications & Email (6 Patterns)

| # | ID | Pattern | Example |
|---|-----|---------|---------|
| 59 | NOTIFY_001 | Duplicate email send | Retry sends 2 emails |
| 60 | NOTIFY_002 | Async error swallowed | Job fails but user not notified |
| 61 | NOTIFY_003 | Notification timing error | "Order complete" email before payment |
| 62 | NOTIFY_004 | Template variable error | `{{user.name}}` is nil |
| 63 | NOTIFY_005 | Recipient mixup | Email sent to wrong user |
| 64 | NOTIFY_006 | Bulk send rate limit | Mass send gets blocked |

### 4.10 Rails-Specific Implicit Knowledge (11 Patterns)

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
| 1-5 | Standard implementation | None (baseline) |
| 6-10 | Complex but correct | Nested transactions, multiple callbacks |
| 11-15 | Non-typical but correct | Intentional design differing from Rails Way |
| 16-20 | Advanced optimization | Correct performance optimization that looks like a bug |

---

## 5. Test Case Generation

### 5.1 Generation Flow

```
[Pattern Definition (Human)] → [Code Generation (AI)] → [Verification (AI)] → [Sample Check (Human)]
```

### 5.2 Pattern Definition File (patterns.yaml)

```yaml
- id: CALC_001
  category: calculation
  name: discount_rate_direction
  plan: "Apply 10% discount for members"
  bug_description: "Discount rate direction wrong, becomes 90% off"
  correct: "total * 0.9"
  incorrect: "total * 0.1"
  severity: critical
  tags: [calculation, discount, member]
```

### 5.3 Generation Prompt

```
Generate e-commerce order processing code based on the following bug pattern.

Pattern: {pattern}
Plan (Specification): {plan}
Bug to inject: {bug_description}

Output:
1. plan.md - Specification document
2. context.md - Existing codebase information
3. impl.rb - Implementation code containing the bug
```

### 5.4 Verification Prompt

```
Review the following code.

Plan: {plan.md}
Context: {context.md}
Code: {impl.rb}

Point out any bugs if present.
```

---

## 6. Technical Architecture

### 6.1 Repository Structure

```
ai-review-benchmark/
├── README.md
├── frameworks/
│   └── rails/
│       ├── patterns.yaml           # Pattern definitions
│       ├── cases/
│       │   ├── CALC_001/
│       │   │   ├── plan.md
│       │   │   ├── context.md
│       │   │   ├── impl.rb
│       │   │   └── meta.json
│       │   ├── CALC_002/
│       │   └── ...
│       └── README.md
├── results/
│   └── rails/
│       └── 2025-01-xx/
│           ├── claude_sonnet.json
│           ├── deepseek_v3.json
│           ├── deepseek_r1.json
│           ├── gemini_pro.json
│           └── report.md
├── scripts/
│   ├── generate_cases.py       # Test case generation
│   ├── run_benchmark.py        # Benchmark execution
│   ├── evaluate_results.py     # Scoring (LLM-as-a-Judge)
│   └── generate_report.py      # Report generation
└── docs/
    ├── methodology.md
    └── patterns.md
```

### 6.2 Case File Specification

#### meta.json
```json
{
  "case_id": "CALC_001",
  "pattern_id": "CALC_001",
  "category": "calculation",
  "name": "discount_rate_direction",
  "difficulty": "easy",
  "expected_detection": true,
  "bug_description": "Discount rate direction wrong, becomes 90% off",
  "bug_location": "impl.rb:15",
  "correct_implementation": "total * 0.9",
  "severity": "critical",
  "tags": ["calculation", "discount", "member"]
}
```

### 6.3 Evaluation Pipeline

```
[Test Case] → [Target Model] → [Review Output] → [Judge Model] → [Score]
                                                      ↓
                                              Claude 3.5 Sonnet
                                              (+ GPT-4o for validation)
```

### 6.4 Metrics

| Metric | Calculation | Target |
|--------|-------------|--------|
| **Recall** | Detections / Total Bugs | > 80% |
| **Precision** | Correct Findings / All Findings | > 70% |
| **False Positive Rate** | False Detections / FP Cases | < 20% |
| **Cost per Review** | API Cost / Case Count | For comparison |
| **Latency** | Average Response Time | Reference |

### 6.5 Category Analysis

Aggregate accuracy by category (Price Calculation, Inventory, State Transitions...) to analyze each model's strengths and weaknesses.

---

## 7. Execution Plan

### 7.1 Phase 1: Preparation (2 days)

- [ ] Initialize repository (PlanStack workspace)
- [ ] Create patterns.yaml (75 patterns)
- [ ] Create generation scripts
- [ ] Manually generate 10 cases to verify format

### 7.2 Phase 2: Case Generation (2 days)

- [ ] AI generates 100 cases
- [ ] Human reviews 20 cases
- [ ] Adjust prompts and regenerate as needed

### 7.3 Phase 3: Pilot (1 day)

- [ ] Run 20 cases with Claude Sonnet
- [ ] Verify Judge accuracy (agreement with human scoring)
- [ ] Adjust Judge prompt as needed

### 7.4 Phase 4: Production Run (2 days)

- [ ] Run 100+ cases with all models
- [ ] Aggregate and analyze results
- [ ] Compare accuracy by category

### 7.5 Phase 5: Writing (2 days)

- [ ] Write Zenn article
- [ ] Create graphs and charts
- [ ] Review and publish

---

## 8. Deliverables

### 8.1 Zenn Article Structure

**Title:**
"Rails AI Code Review: Claude vs DeepSeek Showdown — Detection Power Tested on 100 Real-World Bug Cases"

**Structure:**

1. **Introduction**
   - Why are AI benchmarks mostly "competitive programming"?
   - The missing evaluation criteria for FW app development (90% of real work)
   - "Plan creation → Code generation → Review" all by AI, humans just decide

2. **Methodology**
   - 75 patterns, 100+ cases, 4 models
   - AI-driven test case auto-generation
   - LLM-as-a-Judge evaluation

3. **Results**
   - Overall accuracy comparison
   - Accuracy by category (Price Calculation, Inventory, Authorization...)
   - Cost estimation (monthly cost)
   - Notable detection examples and misses

4. **Discussion**
   - Is DeepSeek V3 production-ready?
   - Strengths and weaknesses by category
   - Did R1's chain-of-thought help?

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
| Low quality generated cases | Reduced reliability | Human reviews 20%, regenerate as needed |
| Low Judge accuracy | Reduced reliability | Compare with human scoring in pilot, multi-Judge validation |
| DeepSeek API instability | Execution delays | Retry mechanism, backup models |
| Unexpected results | Article direction change | Don't jump to conclusions, write based on facts |
| Pattern bias | Reduced generalizability | Distributed across 10 categories, based on real-world experience |

---

## 10. References

### 10.1 Differences from Prior Work

| Name | Target | Task | Difference from This Study |
|------|--------|------|---------------------------|
| HumanEval | Algorithms | Generation | Competitive programming, divorced from practice |
| SWE-bench | OSS Libraries | Generation | Not FW apps |
| SWE-bench Multilingual | Same (multilingual) | Generation | No Rails |
| CodeReviewer | PR Comments | Review | Not spec alignment |
| **This Study** | **Rails Apps** | **Review** | **Plan vs Implementation Alignment** |

### 10.2 Related Links

- [PlanStack](https://plan-stack.ai)
- [DeepSeek API](https://platform.deepseek.com/)
- [Anthropic API](https://docs.anthropic.com/)
- [SWE-bench](https://www.swebench.com/)

---

## Appendix: Pattern List

### A. Price Calculation (10)
CALC_001 – CALC_010

### B. Inventory & Quantity (8)
STOCK_001 – STOCK_008

### C. State Transitions (7)
STATE_001 – STATE_007

### D. User & Authorization (7)
AUTH_001 – AUTH_007

### E. Time & Duration (8)
TIME_001 – TIME_008

### F. External Integration (6)
EXT_001 – EXT_006

### G. Performance (6)
PERF_001 – PERF_006

### H. Data Integrity (6)
DATA_001 – DATA_006

### I. Notifications & Email (6)
NOTIFY_001 – NOTIFY_006

### J. Rails-Specific (11)
RAILS_001 – RAILS_011

### K. False Positive (20)
FP_001 – FP_020

**Total: 95 Patterns (75 Bugs + 20 FP) → 100+ Cases**

---

**Document Version:** 2.0
**Last Updated:** 2025-01-24
