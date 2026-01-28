# Scripts Reference

This document describes all scripts in the `scripts/` directory.

## Core Scripts

### generator.py

Generate test cases from `patterns.yaml` using Claude API.

```bash
# Generate a specific pattern
python scripts/generator.py --pattern CALC_001

# Generate all patterns in a category
python scripts/generator.py --category calculation

# Generate all patterns
python scripts/generator.py --all

# Cost estimate only (no API calls)
python scripts/generator.py --all --dry-run

# Specify framework
python scripts/generator.py --framework django --pattern CALC_001

# Skip confirmation prompt
python scripts/generator.py --all --yes
```

**Options:**
| Option | Description |
|--------|-------------|
| `--pattern` | Generate specific pattern (e.g., `CALC_001`) |
| `--category` | Generate all patterns in a category |
| `--all` | Generate all patterns |
| `--dry-run` | Show cost estimate without generating |
| `--framework` | Target framework: `rails` (default), `django` |
| `--output` | Custom output directory |
| `--model` | Model to use (default: `claude-sonnet-4-20250514`) |
| `--yes`, `-y` | Skip confirmation prompt |

**Generated Files:**
- `plan.md` - Specification document
- `context.md` - Existing codebase context
- `impl.rb` / `impl.py` - Implementation with embedded bug
- `meta.json` - Ground truth metadata

---

### runner.py

Execute benchmark by running AI code reviews on test cases.

```bash
# Run with a specific model
python scripts/runner.py --model claude-sonnet --cases cases/rails/

# Run with specific framework
python scripts/runner.py --model claude-sonnet --framework django

# Run all models
python scripts/runner.py --model all --cases cases/rails/

# Dual mode (explicit + implicit context)
python scripts/runner.py --model claude-sonnet --mode dual

# Dry run (list cases only)
python scripts/runner.py --model claude-sonnet --dry-run
```

**Options:**
| Option | Description |
|--------|-------------|
| `--model` | Model to use: `claude-opus`, `claude-sonnet`, `claude-haiku`, `gpt-4o`, `gpt-5`, `deepseek-v3`, `deepseek-r1`, `gemini-pro`, `gemini-3-pro`, `gemini-3-flash`, `all` |
| `--mode` | Run mode: `explicit` (with guidelines), `implicit` (without), `dual` (both) |
| `--framework` | Framework: `rails` (default), `django`, `laravel` |
| `--cases` | Path to cases directory |
| `--output-dir` | Custom output directory |
| `--verbose`, `-v` | Detailed output |
| `--dry-run` | List cases without API calls |

**Output:**
- `{model}.json` - Raw review results per model
- `summary.json` - Run metadata and statistics

---

### evaluator.py

Score benchmark results using LLM-as-a-Judge.

```bash
# Basic evaluation
python scripts/evaluator.py --run-dir results/20250124_run/

# Skip judge (severity-based scoring only)
python scripts/evaluator.py --run-dir results/xxx/ --skip-judge

# Ensemble judge mode
python scripts/evaluator.py --run-dir results/xxx/ --judge-mode=ensemble --judges=claude,gemini

# Cost estimation
python scripts/evaluator.py --run-dir results/xxx/ --dry-run-cost

# Set budget limit
python scripts/evaluator.py --run-dir results/xxx/ --budget 5.0
```

**Options:**
| Option | Description |
|--------|-------------|
| `--run-dir` | Results directory path (required) |
| `--framework` | Override framework detection |
| `--skip-judge` | Skip LLM judge, use severity-based scoring |
| `--judge-mode` | `single` (default) or `ensemble` |
| `--judges` | Comma-separated judge list (default: `claude,gemini`) |
| `--dry-run-cost` | Estimate cost without running |
| `--budget` | Max budget in dollars |
| `--verbose`, `-v` | Detailed output |

**Output:**
- `report.md` - Human-readable Markdown report
- `evaluations.json` - Detailed per-case evaluations
- `metrics.json` - Aggregated metrics
- `ensemble_details.json` - Ensemble judge details (if applicable)

**Evaluation Modes:**
| Mode | Description |
|------|-------------|
| `severity` | Keyword & severity-based automatic evaluation |
| `semantic` | LLM-based semantic evaluation vs `expected_critique.md` |
| `rubric` | Keyword-based evaluation using `rubric.json` |
| `dual` | Explicit vs implicit context comparison |

---

### generate_catalog.py

Generate case catalog documentation from `meta.json` files.

```bash
# Generate default catalog
python scripts/generate_catalog.py

# Custom output path
python scripts/generate_catalog.py --output docs/my-catalog.md

# Custom cases directory
python scripts/generate_catalog.py --cases-dir cases
```

**Options:**
| Option | Description |
|--------|-------------|
| `--cases-dir` | Path to cases directory (default: `cases`) |
| `--output` | Output file path (default: `docs/case-catalog.md`) |

---

### generate_critique.py

Generate `expected_critique.md` files for semantic evaluation.

```bash
# Generate for a single case
python scripts/generate_critique.py --case CALC_001

# Generate for all cases
python scripts/generate_critique.py --all

# Use LLM for enhanced content
python scripts/generate_critique.py --all --use-llm

# Preview without writing
python scripts/generate_critique.py --case CALC_001 --dry-run

# Overwrite existing files
python scripts/generate_critique.py --all --force
```

**Options:**
| Option | Description |
|--------|-------------|
| `--case` | Process specific case ID |
| `--all` | Process all cases |
| `--use-llm` | Use LLM for enhanced critique generation |
| `--dry-run` | Preview without writing files |
| `--force` | Overwrite existing files |

---

## Migration & Utility Scripts

### update_meta.py

Update `meta.json` files to conform to benchmark spec v3.

```bash
python scripts/update_meta.py
```

**Actions:**
- Adds missing `axis` field based on category
- Extracts `name` from directory name
- Determines `severity` based on tags and description
- Extracts `bug_anchor` from implementation file

---

### migrate_to_dual.py

Migrate test cases to dual-mode evaluation structure.

```bash
# Preview changes
python scripts/migrate_to_dual.py --dry-run

# Apply changes
python scripts/migrate_to_dual.py

# Single case
python scripts/migrate_to_dual.py --case RAILS_001

# Regenerate auto-generated guidelines
python scripts/migrate_to_dual.py --force-regenerate
```

**Options:**
| Option | Description |
|--------|-------------|
| `--dry-run` | Preview without writing |
| `--case` | Process specific case |
| `--verbose`, `-v` | Detailed output |
| `--force-regenerate` | Regenerate auto-generated guidelines |

**Actions:**
- Splits `context.md` into `context_base.md` and `context_guidelines.md`
- Updates `meta.json` with `dual_config` and `fix_validation`
- Generates guidelines from meta if none exist

---

### migrate_must_find.py

Add `must_find` field to `meta.json` files for structured evaluation.

```bash
# Preview changes
python scripts/migrate_must_find.py --dry-run

# Migrate specific case
python scripts/migrate_must_find.py --case CALC_001

# Migrate all cases
python scripts/migrate_must_find.py --all

# Use LLM for better generation
python scripts/migrate_must_find.py --all --use-llm

# Filter by category
python scripts/migrate_must_find.py --all --category calculation
```

**Options:**
| Option | Description |
|--------|-------------|
| `--case` | Migrate specific case |
| `--all` | Migrate all cases |
| `--dry-run` | Preview without writing |
| `--use-llm` | Use LLM for better keyword extraction |
| `--category` | Filter by category |

---

## Supporting Modules

### config.py

Centralized configuration for judge models.

```python
from scripts.config import get_judge_config, estimate_ensemble_cost

# Get judge configuration
config = get_judge_config("claude")
print(config.model_id)  # claude-sonnet-4-20250514

# Estimate ensemble cost
cost = estimate_ensemble_cost(["claude", "gemini"], case_count=100)
print(f"Total: ${cost['total']:.2f}")
```

**Available Judges:**
| Name | Model ID | Provider |
|------|----------|----------|
| `claude` | `claude-sonnet-4-20250514` | Anthropic |
| `gemini` | `gemini-2.5-pro-preview-05-06` | Google |

---

### judges/

Judge implementations for evaluation.

- `base.py` - Abstract base class for judges
- `claude_judge.py` - Claude-based semantic judge
- `gemini_judge.py` - Gemini-based semantic judge
- `ensemble.py` - Ensemble judge combining multiple judges

---

### extractors/

Finding extraction utilities.

- `finding_extractor.py` - Extract findings from AI review output
- `element_matcher.py` - Match findings against ground truth

---

### metrics/

Metrics calculation utilities.

- `fp_metrics.py` - False positive and noise metrics

---

## Typical Workflow

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Generate test cases (if needed)
python scripts/generator.py --framework rails --all --dry-run
python scripts/generator.py --framework rails --all

# 3. Run benchmark
python scripts/runner.py --model claude-sonnet --framework rails

# 4. Evaluate results
python scripts/evaluator.py --run-dir results/20250124_xxxxxx_run/

# 5. Update catalog
python scripts/generate_catalog.py
```

## Environment Variables

Required API keys:

```bash
export ANTHROPIC_API_KEY=xxx   # For Claude models
export OPENAI_API_KEY=xxx      # For GPT models
export DEEPSEEK_API_KEY=xxx    # For DeepSeek models
export GOOGLE_API_KEY=xxx      # For Gemini models
```