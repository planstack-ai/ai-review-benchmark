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
| Claude 3.5 Sonnet | $3.00 | Baseline |
| DeepSeek V3 | $0.14 | Cost Killer |
| DeepSeek R1 | $0.14 | Reasoner |
| Gemini 1.5 Pro | $1.25 | Long Context |

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
export DEEPSEEK_API_KEY=xxx
export GOOGLE_API_KEY=xxx
python scripts/runner.py --model claude-sonnet
```

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
