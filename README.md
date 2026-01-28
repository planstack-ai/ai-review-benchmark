# AI Code Review Benchmark

**Theme:** A framework-agnostic AI review benchmark to verify alignment between specifications (Plan) and implementation (Code)

## Overview

This benchmark quantitatively evaluates the quality of LLM-based code reviews.
Beyond simple bug detection, it measures the advanced review capability of checking **"Is this implemented according to the Plan (design intent)?"**

### Supported Frameworks

| Framework | Cases | Pattern File | Implementation |
|-----------|-------|--------------|----------------|
| Rails | 99 | `patterns.yaml` | `impl.rb` |
| Django | 30 | `patterns_django.yaml` | `impl.py` |
| Laravel | 60 | `patterns_laravel.yaml` | `impl.php` |

### Primary Goal

How reliable is AI as a code reviewer for real-world web applications?

This benchmark evaluates whether AI can:
- detect design and specification violations,
- avoid false positives,
- and provide actionable review feedback
  on production-like code.

### Secondary Goal

Evaluate whether lower-cost models (e.g. DeepSeek V3/R1) can achieve
review quality comparable to state-of-the-art models
at a fraction of the API cost.

### Replacement Criteria

For a lower-cost model to be considered a viable replacement for Claude Sonnet:

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

### Models Under Comparison

| Model | CLI Name | Input ($/1M) | Output ($/1M) | Role |
|-------|----------|--------------|---------------|------|
| Claude Opus 4.5 | `claude-opus` | $5.00 | $25.00 | Anthropic Flagship |
| Claude Sonnet 4 | `claude-sonnet` | $3.00 | $15.00 | Baseline |
| Claude Haiku 4.5 | `claude-haiku` | $1.00 | $5.00 | Anthropic Fast |
| GPT-4o | `gpt-4o` | $2.50 | $10.00 | OpenAI Legacy |
| GPT-5 | `gpt-5` | $1.25 | $10.00 | OpenAI Flagship |
| DeepSeek V3 | `deepseek-v3` | $0.14 | $0.28 | Cost Killer |
| DeepSeek R1 | `deepseek-r1` | $0.55 | $2.19 | Reasoner |
| Gemini 2.5 Pro | `gemini-pro` | $1.25 | $5.00 | Long Context |
| Gemini 3 Pro | `gemini-3-pro` | $1.25 | $5.00 | Latest Gemini |
| Gemini 3 Flash | `gemini-3-flash` | $0.10 | $0.40 | Fast & Cheap |

*Pricing as of January 2025. Check provider docs for current rates.*

## Background: Context Engineering

Traditional code review tools focus on syntax, style, and known bug patterns.
However, **real-world bugs often stem from misunderstanding requirements** -
the code works but doesn't match what was intended.

**Context Engineering** addresses this by providing AI with:
- **Plan (Specification)**: What the code should do
- **Context (Codebase)**: Existing patterns, models, and conventions
- **Implementation**: The code to review

This benchmark measures whether AI can detect the gap between Plan and Code.

## Directory Structure

```
ai-review-benchmark/
├── cases/
│   ├── rails/                 # Rails test cases (99)
│   ├── django/                # Django test cases (30)
│   └── laravel/               # Laravel test cases (60)
├── results/                   # Execution results
├── scripts/
│   ├── config.py              # Model configurations
│   ├── generator.py           # Test case generation
│   ├── runner.py              # Benchmark execution
│   ├── evaluator.py           # Scoring (LLM-as-a-Judge)
│   ├── judges/                # Judge implementations
│   ├── metrics/               # Evaluation metrics
│   └── extractors/            # Response extractors
├── docs/
│   └── benchmark-spec-v3.md   # Full specification
├── patterns.yaml              # Rails bug patterns
├── patterns_django.yaml       # Django bug patterns
├── patterns_laravel.yaml      # Laravel bug patterns
├── CLAUDE.md                  # Claude Code configuration
└── README.md
```

## Test Cases

### Two-Axis Analysis

Results are analyzed along two dimensions:

```
Bug Cases                         Clean Cases
┌──────────────────────┐         ┌─────────────┐
│ Spec Alignment       │         │    FP       │
│ CALC,STOCK,STATE,... │         │             │
├──────────────────────┤         │ Tests       │
│ Implicit Knowledge   │         │ over-       │
│ EXT,PERF,DATA,RAILS  │         │ detection   │
└──────────────────────┘         └─────────────┘
    ↓ DETECTION                      ↓ RESTRAINT
```

| Axis | What it measures |
|------|------------------|
| **Spec Alignment** | Can the model detect Plan vs Code mismatches? |
| **Implicit Knowledge** | Can the model detect issues not written in Plan? |
| **False Positive** | Over-detection test (clean code) |

### Rails Cases (99 total)

| Axis | Categories | Cases |
|------|------------|-------|
| Spec Alignment | CALC, STOCK, STATE, AUTH, TIME, NOTIFY | 47 |
| Implicit Knowledge | EXT, PERF, DATA, RAILS | 39 |
| False Positive | FP | 13 |

| Category | Cases | Verification Points |
|----------|-------|---------------------|
| **CALC** (Price Calculation) | 10 | Discounts, tax, rounding, currency |
| **STOCK** (Inventory) | 8 | Stock allocation, race conditions |
| **STATE** (State Transitions) | 7 | Order status, cancellation, refunds |
| **AUTH** (Authorization) | 7 | Permission checks, access control |
| **TIME** (Time & Duration) | 8 | Timezone, period validation |
| **NOTIFY** (Notifications) | 6 | Duplicate sends, timing, recipients |
| **EXT** (External Integration) | 6 | Payment API, Webhook, idempotency |
| **PERF** (Performance) | 6 | N+1, full table loads, caching |
| **DATA** (Data Integrity) | 6 | Constraints, locking, soft deletes |
| **RAILS** (Rails-Specific) | 15 | Scope, enum, callbacks, transactions |
| **FP** (False Positive) | 13 | Perfect code (test for over-detection) |

### Django Cases (30 MVP)

| Axis | Categories | Cases |
|------|------------|-------|
| Spec Alignment | CALC, AUTH | 17 |
| Implicit Knowledge | DJANGO | 8 |
| False Positive | FP | 5 |

| Category | Cases | Verification Points |
|----------|-------|---------------------|
| **CALC** (Price Calculation) | 10 | Discounts, tax, rounding |
| **AUTH** (Authorization) | 7 | Permission checks, access control |
| **DJANGO** (Django-Specific) | 8 | ORM, signals, middleware, views |
| **FP** (False Positive) | 5 | Perfect code (test for over-detection) |

### Laravel Cases (60)

| Axis | Categories | Cases |
|------|------------|-------|
| Spec Alignment | CALC, AUTH, STOCK, STATE, TIME, NOTIFY | 41 |
| Implicit Knowledge | PERF | 9 |
| False Positive | FP | 10 |

| Category | Cases | Verification Points |
|----------|-------|---------------------|
| **CALC** (Price Calculation) | 10 | Discounts, tax, rounding |
| **AUTH** (Authorization) | 7 | Permission checks, access control |
| **STOCK** (Inventory) | 8 | Stock allocation, race conditions |
| **STATE** (State Transitions) | 6 | Order status, cancellation |
| **TIME** (Time & Duration) | 6 | Timezone, period validation |
| **NOTIFY** (Notifications) | 4 | Duplicate sends, timing |
| **PERF** (Performance) | 9 | N+1, eager loading, caching |
| **FP** (False Positive) | 10 | Perfect code (test for over-detection) |

### Case File Structure

Each case consists of these files:

| File | Description |
|------|-------------|
| `plan.md` | Specification document |
| `context.md` | Existing codebase information |
| `impl.rb` / `impl.py` / `impl.php` | Code under review |
| `meta.json` | Ground truth and metadata |
| `expected_critique.md` | Expected review findings |

## Dual-Mode Evaluation

For **Implicit Knowledge** cases (EXT, PERF, DATA, RAILS), the benchmark supports
comparing AI performance with and without explicit guidelines:

| Mode | Context File | What it tests |
|------|--------------|---------------|
| **Explicit** | `context.md` (with guidelines) | Can AI follow explicit rules? |
| **Implicit** | `context_base.md` (code only) | Can AI infer best practices from code? |

### Running Dual-Mode

```bash
# Explicit mode (default)
python scripts/runner.py --model claude-sonnet --mode explicit

# Implicit mode
python scripts/runner.py --model claude-sonnet --mode implicit

# Dual mode (runs both)
python scripts/runner.py --model claude-sonnet --mode dual
```

### Metrics

- **Inference Gap**: `Explicit Recall - Implicit Recall`
  - Smaller gap = AI can infer best practices (senior engineer level)
- **Fix Accuracy**: Percentage of correct fix suggestions

## Evaluation System

This benchmark uses a **3-layer LLM-as-a-Judge** evaluation system:

### Layer 1: Severity-based (Default)
- Keyword matching for bug detection
- Severity scoring: critical=1.0, major=0.5, minor=0.2

### Layer 2: Rubric-based
- Rule-based evaluation using `rubric.json`
- Structured scoring with predefined criteria

### Layer 3: Semantic Evaluation
- Uses Claude as a judge model
- Compares AI response against `expected_critique.md`
- Evaluates: essential finding captured, severity alignment, suggestion quality
- Scores: 1-5 scale

The evaluation mode is specified in each case's `meta.json`:
- `"evaluation_mode": "severity"` (default)
- `"evaluation_mode": "rubric"`
- `"evaluation_mode": "semantic"`

### Judge Bias Mitigation

To address "Claude judging Claude" bias concerns:

1. **Ensemble Mode**: Uses both Claude + Gemini as judges
   - Score: Mean of semantic scores
   - Detection: Majority vote

2. **Human Validation**: 20 cases validated against human judgment

3. **Transparency**: Judge prompts and model versions published in repository

## Usage

### 1. Environment Setup (Docker recommended)

```bash
# Set up API keys
cp .env.example .env
# Edit .env and enter your API keys

# Build Docker image
docker compose build
```

### 2. Run Benchmark

```bash
# dry-run (list cases)
docker compose run --rm benchmark --model claude-sonnet --dry-run

# Run with single model (Rails - default)
docker compose run --rm benchmark --model claude-sonnet

# Run with specific framework
docker compose run --rm benchmark --model claude-sonnet --framework django
docker compose run --rm benchmark --model claude-sonnet --framework laravel

# Run with all models
docker compose run --rm benchmark --model all

# Run specific category only
docker compose run --rm benchmark --model claude-sonnet --cases cases/rails/CALC_001
```

### 3. Scoring & Report Generation

```bash
docker compose run --rm benchmark python scripts/evaluator.py --run-dir results/{timestamp}_run
```

### Local Execution (without Docker)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=xxx
export OPENAI_API_KEY=xxx
export DEEPSEEK_API_KEY=xxx
export GOOGLE_API_KEY=xxx

# Run benchmark (Rails - default)
python scripts/runner.py --model claude-sonnet

# Run benchmark with specific framework
python scripts/runner.py --model claude-sonnet --framework django
python scripts/runner.py --model claude-sonnet --framework laravel
```

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

## Example Results

> **Note**: Sample data for illustration. Run `python scripts/evaluator.py` for actual results.

### Sample Report Output

| Model | Recall | Weighted Recall | Case-FPR | Cost |
|-------|--------|-----------------|----------|------|
| claude-sonnet | 85.2% | 72.4% | 15.0% | $2.85 |
| deepseek-v3 | 79.8% | 65.3% | 22.5% | $0.14 |

### By Category Performance

| Category | Detected/Total | Accuracy |
|----------|----------------|----------|
| CALC (Price) | 9/10 | 90.0% |
| RAILS | 11/11 | 85.0% |
| EXT (External) | 6/6 | 93.3% |
| TIME | 8/8 | 92.5% |
| AUTH | 6/7 | 91.4% |

### Key Findings

- High recall (89%) on bug cases
- Strong performance on Rails-specific patterns
- Room for improvement in fix suggestion quality

### What Good Looks Like

Example of successful detection (CALC_001 - Discount calculation bug):

**Bug Code:**
```ruby
def apply_member_discount
  @subtotal * MEMBER_DISCOUNT_RATE  # Bug: 0.10 = 90% off!
end
```

**Expected AI Response:**
```json
{
  "bugs_found": true,
  "issues": [{
    "severity": "critical",
    "description": "Discount calculation is inverted - multiplying by 0.10 gives 90% discount instead of 10%",
    "suggestion": "Use @subtotal * (1 - MEMBER_DISCOUNT_RATE) or @subtotal * 0.90"
  }]
}
```

**Scoring**: Detected = TP, Severity match = +1.0 weighted score

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
| **Cost per Review** | API Cost / 99 cases | For comparison |

**Detection Score by Severity**: critical=1.0, major=0.5, minor=0.2

> **Note**: All metrics are **macro averages** (averaged across cases).

## Documentation

- [Full Specification (v3)](docs/benchmark-spec-v3.md) - Detailed benchmark design and bug patterns
- [CLAUDE.md](CLAUDE.md) - Project guide for Claude Code

## License

MIT License

## Related Links

- [PlanStack](https://plan-stack.ai)
