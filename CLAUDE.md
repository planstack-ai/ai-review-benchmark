# AI Review Benchmark

Benchmark for evaluating AI code review quality on Rails applications.

> Full specification: [docs/benchmark-spec-v3.md](docs/benchmark-spec-v3.md)

## Rules

- Use **English** for all code, comments, commits, and documentation
- Python: 3.11+, type hints, black, ruff, Google-style docstrings
- Ruby: 3.2+ / Rails 7.1+, rubocop compliant

### Planning Workflow

1. **Always write plans in `docs/plans/`** before implementing any feature or change
2. **Do NOT start writing code** until the plan is approved by the user
3. **After plan approval**, save the final plan in `docs/plans/` with a descriptive filename (e.g., `docs/plans/feature-xyz.md`)

## Quick Reference

### Commands

```bash
# Generate test case
python scripts/generator.py --pattern CALC_001

# Run benchmark
python scripts/runner.py --model claude-sonnet --cases cases/rails/

# Score results
python scripts/evaluator.py --run-dir results/2025xxxx_run/
```

### Environment Variables

```bash
export ANTHROPIC_API_KEY=xxx
export OPENAI_API_KEY=xxx
export DEEPSEEK_API_KEY=xxx
export GOOGLE_API_KEY=xxx
```

## Project Structure

```
cases/rails/{CASE_ID}/
├── plan.md      # Specification
├── context.md   # Existing codebase info
├── impl.rb      # Code under review
└── meta.json    # Ground truth
```

## Test Cases (99 total)

| Axis | Categories | Cases |
|------|------------|-------|
| Spec Alignment | CALC, STOCK, STATE, AUTH, TIME, NOTIFY | 46 |
| Implicit Knowledge | EXT, PERF, DATA, RAILS | 33 |
| False Positive | FP | 20 |

## Evaluation Targets

| Metric | Target |
|--------|--------|
| Recall | > 80% |
| Precision | > 70% |
| False Positive Rate | < 20% |

## meta.json Schema

```json
{
  "case_id": "CALC_001",
  "category": "calculation",
  "axis": "spec_alignment | implicit_knowledge",
  "name": "discount_rate_direction",
  "difficulty": "easy | medium | hard",
  "expected_detection": true,
  "bug_description": "...",
  "bug_anchor": "code snippet to match",
  "correct_implementation": "...",
  "severity": "critical | high | medium | low",
  "tags": ["calculation", "discount"]
}
```