# CLAUDE.md - AI Review Benchmark Project Guide

> **Full Specification:** See [docs/benchmark-spec-v3.md](docs/benchmark-spec-v3.md)

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
| Claude Sonnet 4 | $3.00 | Baseline |
| GPT-4o | $2.50 | OpenAI Flagship |
| GPT-4o mini | $0.15 | OpenAI Cost Efficient |
| DeepSeek V3 | $0.14 | Cost Killer |
| DeepSeek R1 | $0.55 | Reasoner |
| Gemini 2.5 Pro | $1.25 | Long Context |
| Gemini 3 Pro | $1.25 | Latest Gemini |
| Gemini 3 Flash | $0.10 | Fast & Cheap |

## Test Case Structure (v3: 95 cases)

### Two-Axis Analysis

| Axis | Categories | Cases | What it measures |
|------|------------|-------|------------------|
| **Spec Alignment** | CALC, STOCK, STATE, AUTH, TIME, NOTIFY | 46 | Plan vs Code mismatches |
| **Implicit Knowledge** | EXT, PERF, DATA, RAILS | 29 | Issues not written in Plan |
| **False Positive** | FP | 20 | Over-detection test |

### By Category

| Category | Cases | Axis |
|----------|-------|------|
| Price Calculation (CALC) | 10 | Spec Alignment |
| Inventory & Quantity (STOCK) | 8 | Spec Alignment |
| State Transitions (STATE) | 7 | Spec Alignment |
| User & Authorization (AUTH) | 7 | Spec Alignment |
| Time & Duration (TIME) | 8 | Spec Alignment |
| Notifications & Email (NOTIFY) | 6 | Spec Alignment |
| External Integration (EXT) | 6 | Implicit Knowledge |
| Performance (PERF) | 6 | Implicit Knowledge |
| Data Integrity (DATA) | 6 | Implicit Knowledge |
| Rails-Specific (RAILS) | 11 | Implicit Knowledge |
| False Positive (FP) | 20 | - |

## Evaluation Metrics

| Metric | Calculation | Target |
|--------|-------------|--------|
| **Recall** | TP / (TP + FN) | > 80% |
| **Precision** | TP / (TP + FP) | > 70% |
| **False Positive Rate** | FP cases flagged / 20 | < 20% |
| **Noise Rate** | Extra findings / Total findings | Reference |
| **Cost per Review** | API Cost / 95 cases | For comparison |

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
cases/rails/{CASE_ID}/
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
  "case_id": "CALC_001",
  "category": "calculation",
  "axis": "spec_alignment | implicit_knowledge",
  "name": "discount_rate_direction",
  "difficulty": "easy | medium | hard",
  "expected_detection": true | false,
  "bug_description": "Description of the issue",
  "bug_anchor": "code snippet to match",
  "correct_implementation": "Correct implementation example",
  "severity": "critical | high | medium | low",
  "tags": ["calculation", "discount"]
}
```

## Commands

### Test Case Generation
```bash
python scripts/generator.py --pattern CALC_001
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
export OPENAI_API_KEY=xxx
export DEEPSEEK_API_KEY=xxx
export GOOGLE_API_KEY=xxx
```

## Key Design Decisions

1. **Judge Model**: Claude 3.5 Sonnet with 20-case human validation
2. **Evaluation Format**: JSON output for quantitative evaluation
3. **Two-Axis Analysis**: Spec Alignment vs Implicit Knowledge
4. **Bug Anchor**: String match instead of line numbers for robustness

## Disclaimers

- **Single execution**: Models run once with temperature=0
- **Judge model**: Claude 3.5 Sonnet; human validation on 20 cases
- **AI-generated cases**: 20 cases human-reviewed for realism
- **Rails-specific**: Results may not generalize to other frameworks
