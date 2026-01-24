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
│       ├── plan_mismatch/     # Plan misalignment (20 cases)
│       ├── logic_bug/         # Logic bugs (20 cases)
│       └── false_positive/    # Perfect code (20 cases)
├── results/                   # Execution results
├── scripts/
│   ├── generator.py           # Test case generation
│   ├── runner.py              # Benchmark execution
│   └── evaluator.py           # Scoring (LLM-as-a-Judge)
├── CLAUDE.md                  # Claude Code configuration
└── README.md
```

## Test Cases

### Category Composition (60 cases total)

| Category | Cases | Verification Points |
|----------|-------|---------------------|
| **Plan Mismatch** | 20 | Not implemented according to spec (code runs fine) |
| **Logic Bug** | 20 | N+1, transactions, security |
| **False Positive** | 20 | Perfect code (test for over-detection) |

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
docker compose run --rm benchmark --model claude-sonnet --cases cases/rails/plan_mismatch
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
| **Recall** | Detections / Total Bugs | > 80% |
| **Precision** | Correct Findings / All Findings | > 70% |
| **False Positive Rate** | False Detections / FP Cases | < 20% |
| **Cost per Review** | API Cost / Case Count | For comparison |

## License

MIT License

## Related Links

- [PlanStack](https://plan-stack.ai)
