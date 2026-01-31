# AI Review Benchmark

Benchmark for evaluating AI code review quality on Rails, Django, Laravel, and Spring Boot (Java/Kotlin) applications.

> Full specification: [docs/benchmark-spec-v3.md](docs/benchmark-spec-v3.md)

## Rules

- Use **English** for all code, comments, commits, and documentation
- Python: 3.11+, type hints, black, ruff, Google-style docstrings
- Ruby: 3.2+ / Rails 7.1+, rubocop compliant
- Java: 21+ / Spring Boot 3.2+, standard Java conventions
- Kotlin: 1.9+ / Spring Boot 3.2+, idiomatic Kotlin style
- PHP: 8.2+ / Laravel 11+, PSR-12 compliant

### Planning Workflow

1. **Always write plans in `docs/plans/`** before implementing any feature or change
2. **Do NOT start writing code** until the plan is approved by the user
3. **After plan approval**, save the final plan in `docs/plans/` with a descriptive filename (e.g., `docs/plans/feature-xyz.md`)

## Quick Reference

### Commands

**Always activate venv first:** `source .venv/bin/activate`

```bash
# Generate test case (Rails - default)
python scripts/generator.py --pattern CALC_001

# Generate test case (Django / Laravel)
python scripts/generator.py --framework django --pattern CALC_001
python scripts/generator.py --framework laravel --pattern CALC_001

# Generate test case (Spring Boot - Java)
python scripts/generator.py --framework springboot-java --pattern CALC_001

# Run benchmark (Rails - default)
python scripts/runner.py --model claude-sonnet --cases cases/rails/

# Run benchmark (Django / Laravel)
python scripts/runner.py --model claude-sonnet --framework django
python scripts/runner.py --model claude-sonnet --framework laravel

# Run benchmark (Spring Boot - Java)
python scripts/runner.py --model claude-sonnet --framework springboot-java

# Run benchmark (Spring Boot - Kotlin)
python scripts/runner.py --model claude-sonnet --framework springboot-kotlin

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
cases/{framework}/{CASE_ID}/
├── plan.md      # Specification
├── context.md   # Existing codebase info
├── impl.rb      # Code under review (Rails)
├── impl.py      # Code under review (Django)
├── impl.php     # Code under review (Laravel)
├── impl.java    # Code under review (Spring Boot - Java)
├── impl.kt      # Code under review (Spring Boot - Kotlin)
└── meta.json    # Ground truth
```

## Supported Frameworks

| Framework | Pattern File | Cases Dir | Implementation |
|-----------|--------------|-----------|----------------|
| Rails | patterns.yaml | cases/rails/ | impl.rb |
| Django | patterns_django.yaml | cases/django/ | impl.py |
| Laravel | - | cases/laravel/ | impl.php |
| Laravel | patterns_laravel.yaml | cases/laravel/ | impl.php |
| Spring Boot (Java) | patterns_springboot_java.yaml | cases/springboot-java/ | impl.java |
| Spring Boot (Kotlin) | patterns_springboot_kotlin.yaml | cases/springboot-kotlin/ | impl.kt |

## Test Cases

### Rails (99 total)

| Axis | Categories | Cases |
|------|------------|-------|
| Spec Alignment | CALC, STOCK, STATE, AUTH, TIME, NOTIFY | 47 |
| Implicit Knowledge | EXT, PERF, DATA, RAILS | 39 |
| False Positive | FP | 13 |

### Django (30 MVP)

| Axis | Categories | Cases |
|------|------------|-------|
| Spec Alignment | CALC, AUTH | 17 |
| Implicit Knowledge | DJANGO | 8 |
| False Positive | FP | 5 |

### Spring Boot - Java (55 total)

| Axis | Categories | Cases |
|------|------------|-------|
| Spec Alignment | CALC, AUTH, STATE, TIME, STOCK, NOTIFY | 20 |
| Implicit Knowledge | SPRING, PERF, DATA, EXT | 30 |
| False Positive | FP | 5 |

### Spring Boot - Kotlin (98 total)

| Axis | Categories | Cases |
|------|------------|-------|
| Spec Alignment | CALC, AUTH, STATE, TIME, STOCK, NOTIFY | 46 |
| Implicit Knowledge | SPRING, PERF, DATA, EXT | 39 |
| False Positive | FP | 13 |

### Laravel (60)

| Axis | Categories | Cases |
|------|------------|-------|
| Spec Alignment | CALC, STOCK, STATE, AUTH, TIME, NOTIFY | 41 |
| Implicit Knowledge | PERF | 9 |
| False Positive | FP | 10 |

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
  "tags": ["calculation", "discount"],
  "framework": "django | springboot-java | springboot-kotlin",
  "framework_version": "5.0+ | 3.2+",
  "python_version": "3.11+",           // Django only
  "java_version": "21+",               // Spring Boot (Java) only
  "kotlin_version": "1.9+",            // Spring Boot (Kotlin) only
  "framework": "django | laravel", // Django/Laravel only
  "framework_version": "5.0+",     // Django/Laravel only
  "python_version": "3.11+",       // Django only
  "php_version": "8.2+"            // Laravel only
}
```
