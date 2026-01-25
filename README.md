# AI Code Review Benchmark: Rails × Context Engineering Edition

**Theme:** A Rails-specific AI review benchmark to verify alignment between specifications (Plan) and implementation (Code)

## Overview

This benchmark quantitatively evaluates the quality of LLM-based code reviews.
Beyond simple bug detection, it measures the advanced review capability of checking **"Is this implemented according to the Plan (design intent)?"**

### Primary Goal

**Can DeepSeek replace Claude Sonnet?**

Quantitatively verify whether DeepSeek V3/R1, at 1/20th the API cost, can deliver production-quality code review.

### Models Under Comparison

| Model | Cost ($/1M input) | Role |
|-------|-------------------|------|
| Claude Sonnet 4 | $3.00 | Baseline |
| GPT-4o | $2.50 | OpenAI Flagship |
| GPT-4o mini | $0.15 | OpenAI Cost Efficient |
| DeepSeek V3 | $0.14 | Cost Killer |
| DeepSeek R1 | $0.55 | Reasoner |
| Gemini 2.5 Pro | $1.25 | Long Context |
| Gemini 3 Pro | $1.25 | Latest Gemini |
| Gemini 3 Flash | $0.10 | Fast & Cheap |

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
│   └── rails/
│       ├── CALC_001/          # Price calculation cases
│       ├── STOCK_001/         # Inventory & quantity cases
│       ├── STATE_001/         # State transition cases
│       ├── AUTH_001/          # Authorization cases
│       ├── TIME_001/          # Time & duration cases
│       ├── NOTIFY_001/        # Notification cases
│       ├── EXT_001/           # External integration cases
│       ├── PERF_001/          # Performance cases
│       ├── DATA_001/          # Data integrity cases
│       ├── RAILS_001/         # Rails-specific cases
│       ├── FP_001/            # False positive cases
│       └── ...                # 95 cases total
├── results/                   # Execution results
├── scripts/
│   ├── generator.py           # Test case generation
│   ├── runner.py              # Benchmark execution
│   └── evaluator.py           # Scoring (LLM-as-a-Judge)
├── docs/
│   └── benchmark-spec-v3.md   # Full specification
├── patterns.yaml              # Bug pattern definitions
├── CLAUDE.md                  # Claude Code configuration
└── README.md
```

## Test Cases

### Two-Axis Analysis

Results are analyzed along two dimensions:

| Axis | Categories | Cases | What it measures |
|------|------------|-------|------------------|
| **Spec Alignment** | CALC, STOCK, STATE, AUTH, TIME, NOTIFY | 46 | Can the model detect Plan vs Code mismatches? |
| **Implicit Knowledge** | EXT, PERF, DATA, RAILS | 29 | Can the model detect issues not written in Plan? |
| **False Positive** | FP | 20 | Over-detection test |

### Category Composition (95 cases total)

| Category | Cases | Axis | Verification Points |
|----------|-------|------|---------------------|
| **CALC** (Price Calculation) | 10 | Spec Alignment | Discounts, tax, rounding, currency |
| **STOCK** (Inventory) | 8 | Spec Alignment | Stock allocation, race conditions |
| **STATE** (State Transitions) | 7 | Spec Alignment | Order status, cancellation, refunds |
| **AUTH** (Authorization) | 7 | Spec Alignment | Permission checks, access control |
| **TIME** (Time & Duration) | 8 | Spec Alignment | Timezone, period validation |
| **NOTIFY** (Notifications) | 6 | Spec Alignment | Duplicate sends, timing, recipients |
| **EXT** (External Integration) | 6 | Implicit Knowledge | Payment API, Webhook, idempotency |
| **PERF** (Performance) | 6 | Implicit Knowledge | N+1, full table loads, caching |
| **DATA** (Data Integrity) | 6 | Implicit Knowledge | Constraints, locking, soft deletes |
| **RAILS** (Rails-Specific) | 11 | Implicit Knowledge | Scope, enum, callbacks, transactions |
| **FP** (False Positive) | 20 | - | Perfect code (test for over-detection) |

### Case File Structure

Each case consists of 4 files:

- `plan.md` - Specification document (requirements to reference during review)
- `context.md` - Existing codebase information
- `impl.rb` - Code under review
- `meta.json` - Ground truth and metadata

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

# Run with single model
docker compose run --rm benchmark --model claude-sonnet
docker compose run --rm benchmark --model deepseek-v3
docker compose run --rm benchmark --model deepseek-r1
docker compose run --rm benchmark --model gemini-pro

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
python scripts/runner.py --model claude-sonnet
```

## Example Results

### Sample Report Output

| Model | Recall | Weighted Recall | FPR | Cost |
|-------|--------|-----------------|-----|------|
| claude-sonnet | 89.3% | 66.1% | 100.0% | $2.21 |

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

## Evaluation Metrics

| Metric | Calculation | Target |
|--------|-------------|--------|
| **Recall** | TP / (TP + FN) | > 80% |
| **Precision** | TP / (TP + FP) | > 70% |
| **False Positive Rate** | FP cases flagged / 20 FP cases | < 20% |
| **Noise Rate** | Extra findings / Total findings | Reference |
| **Cost per Review** | API Cost / 95 cases | For comparison |

## Documentation

- [Full Specification (v3)](docs/benchmark-spec-v3.md) - Detailed benchmark design and bug patterns
- [CLAUDE.md](CLAUDE.md) - Project guide for Claude Code

## License

MIT License

## Related Links

- [PlanStack](https://plan-stack.ai)
