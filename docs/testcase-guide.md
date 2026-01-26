# Test Case Creation Guide

This guide explains how to create new test cases for the AI Code Review Benchmark.

## Core Principles

1. **One case = one issue** - Each test case should contain exactly one bug or test one specific FP scenario
2. **Natural-looking code** - Bugs should be subtle mistakes a developer might make, not obvious errors
3. **Verifiable requirements** - The spec in `plan.md` must clearly define what the code should do

## File-by-File Guidelines

### plan.md

The specification document that defines requirements.

**Structure:**
```markdown
# Feature Name

## Overview
Brief description of what this feature/service does.

## Requirements
1. Requirement one
2. Requirement two
3. ...

## Constraints
- Constraint one
- Constraint two

## References
- Related models/services
- External API docs if applicable
```

**Do:**
- Write clear, numbered requirements
- Include boundary conditions and edge cases
- Reference existing code patterns from `context.md`
- Use precise language ("must", "should", "when X, then Y")

**Don't:**
- Include implementation hints
- Mention the bug or correct solution
- Use vague requirements

### context.md

Provides existing codebase information.

**Content:**
- Schema definitions (tables, columns, types)
- Related model code with scopes and methods
- Existing service patterns in the codebase
- Constants and configuration values

**Guidelines:**
- Include realistic scopes and helper methods
- Provide enough context for the reviewer to understand the codebase
- Target 100-150 lines of context
- Include comments that exist in a real codebase

**Example:**
```markdown
# Existing Codebase

## Schema
```ruby
# orders table
# - id: bigint
# - user_id: bigint (foreign key)
# - status: integer (enum)
# - total: decimal(10,2)
```

## Order Model
```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items

  enum status: { pending: 0, confirmed: 1, shipped: 2 }

  scope :active, -> { where.not(status: :canceled) }

  def apply_discount(rate)
    self.total = total * (1 - rate)
  end
end
```
```

### impl.rb / impl.php / impl.py

The code under review.

**Guidelines:**
- 30-80 lines of code
- Use service class pattern (e.g., `OrderCalculationService`)
- Bug should be subtle, not an obvious typo
- Code should look professional and follow conventions
- No hint comments (avoid `# TODO`, `# FIXME`, `# BUG`)

**Bug Placement Tips:**
- Off-by-one errors in boundary checks
- Wrong operator (`>` vs `>=`, `*` vs `/`)
- Missing validation or authorization check
- Incorrect order of operations
- Missing nil/null checks

**Don't:**
- Include multiple bugs in one case
- Add comments that hint at the bug
- Write obviously broken code
- Include unrelated code that distracts from the bug

### meta.json

Ground truth and metadata for the case.

#### Bug Case Fields

```json
{
  "case_id": "CALC_001",
  "category": "calculation",
  "axis": "spec_alignment",
  "name": "discount_rate_direction",
  "difficulty": "easy",
  "expected_detection": true,
  "bug_description": "Discount rate direction wrong, becomes 90% off",
  "bug_anchor": "total * 0.1",
  "correct_implementation": "total * 0.9",
  "severity": "critical",
  "tags": ["calculation", "discount", "member"],
  "evaluation_mode": "severity"
}
```

#### FP Case Fields

```json
{
  "case_id": "FP_001",
  "category": "false_positive",
  "axis": null,
  "name": "standard_crud",
  "difficulty": "easy",
  "expected_detection": false,
  "bug_description": null,
  "bug_anchor": null,
  "correct_implementation": "Standard RESTful controller",
  "severity": null,
  "tags": ["false_positive", "crud", "baseline"],
  "evaluation_mode": "semantic"
}
```

#### Django-Specific Fields

Django cases require additional fields:

```json
{
  "framework": "django",
  "framework_version": "5.0+",
  "python_version": "3.11+"
}
```

#### Laravel-Specific Fields

Laravel cases require additional fields:

```json
{
  "framework": "laravel",
  "framework_version": "11.0+",
  "php_version": "8.2+"
}
```

#### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `case_id` | string | Yes | Unique identifier (e.g., `CALC_001`) |
| `category` | string | Yes | Category name (e.g., `calculation`, `false_positive`) |
| `axis` | string\|null | Yes | `spec_alignment`, `implicit_knowledge`, or `null` for FP |
| `name` | string | Yes | Short descriptive name (snake_case) |
| `difficulty` | string | Yes | `easy`, `medium`, or `hard` |
| `expected_detection` | boolean | Yes | `true` for bug cases, `false` for FP |
| `bug_description` | string\|null | Bug only | Human-readable bug description |
| `bug_anchor` | string\|null | Bug only | Code snippet containing the bug |
| `correct_implementation` | string | Yes | Correct code or description |
| `severity` | string\|null | Bug only | `critical`, `high`, `medium`, or `low` |
| `tags` | array | Yes | Relevant tags for categorization |
| `evaluation_mode` | string | No | `severity` (default), `semantic`, or `dual` |

### expected_critique.md

Expected review findings for semantic evaluation.

#### Bug Case Structure

```markdown
# Expected Critique

## Essential Finding
[Concise description of the bug and its impact]

## Key Points to Mention
1. **Bug Location**: Where the bug is in the code
2. **Incorrect Logic**: What the code does wrong
3. **Correct Implementation**: How to fix it
4. **Business Impact**: Consequences of the bug
5. **Related Effects**: Any cascading issues

## Severity Rationale
- **Financial Impact**: Revenue/cost implications
- **Scope**: How many users/transactions affected
- **Production Risk**: Consequences if deployed

## Acceptable Variations
- Different fix approaches that are also correct
- Alternative terminology to describe the bug
- Different aspects reviewers might emphasize
```

#### FP Case Structure

```markdown
# Expected Critique

## Expected Behavior
[Description of what the code correctly does]

## What Makes This Code Correct
- [Reason 1]
- [Reason 2]
- [Reason 3]

## Acceptable Feedback
[Types of minor suggestions that are okay]

## What Should NOT Be Flagged
- **[Pattern 1]**: Why it's correct
- **[Pattern 2]**: Why it's correct

## False Positive Triggers
- [Pattern that might incorrectly trigger AI flags]
```

## FP Case Guidelines

False Positive cases test whether AI over-detects bugs.

### FP Categories

| Type | Description | Examples |
|------|-------------|----------|
| **Standard** (FP_001-005) | Clean, conventional code | Basic CRUD, simple services |
| **Complex but correct** (FP_006-010) | Sophisticated patterns | Nested transactions, callbacks |
| **Non-typical but correct** (FP_011-015) | Unconventional approaches | Custom patterns, workarounds |
| **Advanced optimization** (FP_016-020) | Performance patterns | Caching, batch operations |

### What Makes a Good FP Case

1. **Looks suspicious but isn't** - Code that might trigger false alarms
2. **Real-world patterns** - Actual code patterns from production apps
3. **Documented reasoning** - `expected_critique.md` explains why it's correct
4. **Edge case handling** - Covers scenarios that might confuse AI

### FP Red Flags to Include

- Complex conditionals that are actually correct
- Performance optimizations that look like bugs
- Intentional design decisions that differ from conventions
- Edge case handling that seems incomplete but isn't

## Verification Checklist

Before submitting a new case, verify:

### File Completeness
- [ ] `plan.md` exists and has clear requirements
- [ ] `context.md` provides sufficient codebase context
- [ ] `impl.rb` or `impl.py` exists (30-80 lines)
- [ ] `meta.json` has all required fields
- [ ] `expected_critique.md` exists

### Bug Case Verification
- [ ] Bug matches `bug_description` in meta.json
- [ ] `bug_anchor` appears exactly in impl file
- [ ] Bug is subtle, not obvious
- [ ] Only one bug per case
- [ ] Severity is appropriate

### FP Case Verification
- [ ] Code is actually correct
- [ ] `expected_detection` is `false`
- [ ] `expected_critique.md` explains why it's correct
- [ ] Code looks suspicious enough to potentially trigger false alarms

### Meta.json Validation
- [ ] `case_id` matches directory name
- [ ] `axis` is correct for category
- [ ] `tags` are relevant and accurate
- [ ] Django cases have framework-specific fields

### Cross-Reference Check
- [ ] Requirements in `plan.md` are testable
- [ ] Context in `context.md` is referenced in impl
- [ ] Implementation uses patterns from context
- [ ] Expected critique matches actual bug/behavior

## Example Case Structure

**Rails:**
```
cases/rails/CALC_001/
├── plan.md              # "Members get 10% discount on orders"
├── context.md           # Order model with apply_discount method
├── impl.rb              # Bug: total * 0.1 instead of total * 0.9
├── meta.json            # severity: critical, axis: spec_alignment
└── expected_critique.md # Explains the inverted discount logic
```

**Laravel:**
```
cases/laravel/CALC_001/
├── plan.md              # "Members get 10% discount on orders"
├── context.md           # Order model with discount calculation
├── impl.php             # Bug: $total * 0.1 instead of $total * 0.9
├── meta.json            # severity: critical, framework: laravel
└── expected_critique.md # Explains the inverted discount logic
```

**Django:**
```
cases/django/CALC_001/
├── plan.md              # "Members get 10% discount on orders"
├── context.md           # Order model with discount method
├── impl.py              # Bug: total * Decimal('0.1') instead of 0.9
├── meta.json            # severity: critical, framework: django
└── expected_critique.md # Explains the inverted discount logic
```

## Tips for Writing Cases

1. **Start with the bug** - Design the case around a specific bug pattern
2. **Work backwards** - Write `plan.md` to establish the requirement the bug violates
3. **Add realistic context** - Include helper methods and scopes that could help
4. **Test your case** - Run the benchmark on your case to verify detection
5. **Get a second opinion** - Have someone else review if the bug is detectable

## Common Mistakes to Avoid

- Creating cases where the bug is too obvious
- Including multiple bugs that confuse the evaluation
- Writing vague requirements that don't clearly specify behavior
- Missing `bug_anchor` that doesn't match the actual code
- FP cases that actually have real bugs
