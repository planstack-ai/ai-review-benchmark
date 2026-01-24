# CLAUDE.md - AI Review Benchmark Project Guide

> **Full Specification:** See [docs/benchmark-spec-v2.md](docs/benchmark-spec-v2.md)

## Language

**Use English for all code, comments, commit messages, and documentation.**

## Project Overview

A benchmark project for evaluating AI code review quality on Rails applications.
Demonstrates the effectiveness of Context Engineering by verifying alignment between Plan (specification) and Code (implementation).

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

## Test Case Structure (v2: 95 patterns → 100+ cases)

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
| **False Positive** | 20 | No bugs (over-detection test) |

## Evaluation Metrics

| Metric | Calculation | Target |
|--------|-------------|--------|
| **Recall** | Detections / Total Bugs | > 80% |
| **Precision** | Correct Findings / All Findings | > 70% |
| **False Positive Rate** | False Detections / FP Cases | < 20% |
| **Cost per Review** | API Cost / Case Count | For comparison |

## Coding Standards

### Python (Scripts)

- Python 3.11+
- Type hints required
- Formatter: black
- Linter: ruff
- Docstrings: Google style

### Ruby (Test Cases)

- Ruby 3.2+ / Rails 7.1+
- Follow standard Rails conventions
- rubocop compliant

## Directory Structure

```
cases/rails/{category}/{case_id}/
├── plan.md      # Specification
├── context.md   # Existing codebase info
├── impl.rb      # Code under review
└── meta.json    # Ground truth
```

## Test Case Creation Guidelines

### plan.md

- Clearly state requirements the implementer should follow
- Specify existing methods/scopes to use in "Existing Implementation" section
- Remove ambiguity, write in verifiable form

### context.md

- Information about existing models, methods, scopes
- "Codebase knowledge" that the reviewer (AI) can reference
- Structured as if from a real Rails project

### impl.rb

- Code under review (Service, Controller, Model, etc.)
- Implementation against plan.md requirements
- Bug cases contain 1-2 issues

### meta.json

```json
{
  "case_id": "plan_mismatch_01",
  "category": "plan_mismatch | logic_bug | false_positive",
  "difficulty": "easy | medium | hard",
  "expected_detection": true | false,
  "bug_description": "Description of the issue",
  "bug_location": "impl.rb:line_number",
  "correct_implementation": "Correct implementation example",
  "tags": ["calculation", "discount"],
  "notes": "Additional notes"
}
```

## Commands

### Test Case Generation
```bash
python scripts/generator.py --category plan_mismatch --count 20
```

### Benchmark Execution
```bash
python scripts/runner.py --model claude-sonnet --cases cases/rails/
```

### Scoring
```bash
python scripts/evaluator.py --run-dir results/2025xxxx_run/
```

## API Configuration

Set API keys via environment variables:

```bash
export ANTHROPIC_API_KEY=xxx
export DEEPSEEK_API_KEY=xxx
export GOOGLE_API_KEY=xxx
```

## Key Design Decisions

1. **Judge Model**: Uses Claude 3.5 Sonnet (+ GPT-4o for cross-validation)
2. **Evaluation Format**: Quantitative evaluation via JSON output (eliminates natural language ambiguity)
3. **Case Independence**: Each case is designed to be evaluated independently

## Notes

- Test cases are created for benchmarking, not from real Rails code
- Bugs are intentionally injected, not actual security vulnerabilities
- Results are point-in-time snapshots; may vary with model updates
