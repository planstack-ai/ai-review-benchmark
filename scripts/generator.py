#!/usr/bin/env python3
"""Generate test cases from patterns.yaml using Claude API.

Usage:
    python scripts/generator.py --pattern CALC_001
    python scripts/generator.py --category calculation
    python scripts/generator.py --all
    python scripts/generator.py --all --dry-run  # Cost estimate only
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(Path(__file__).parent.parent / ".env")

# anthropic is imported lazily to allow --dry-run without the package
anthropic = None

DEFAULT_MODEL = "claude-sonnet-4-20250514"  # Use Sonnet for cost efficiency, Opus for quality
MAX_TOKENS = 4096

# Pricing (per 1M tokens)
INPUT_PRICE = 3.00  # Sonnet
OUTPUT_PRICE = 15.00  # Sonnet

# Global config (set by main)
CONFIG = {"model": DEFAULT_MODEL, "framework": "rails"}

# Framework-specific configuration
FRAMEWORK_CONFIG = {
    "rails": {
        "impl_ext": ".rb",
        "language": "Ruby",
        "expert_role": "Senior Ruby on Rails developer",
        "orm": "ActiveRecord",
        "patterns_file": "patterns.yaml",
    },
    "django": {
        "impl_ext": ".py",
        "language": "Python",
        "expert_role": "Senior Django developer",
        "orm": "Django ORM",
        "patterns_file": "patterns_django.yaml",
    },
    "springboot-java": {
        "impl_ext": ".java",
        "language": "Java",
        "expert_role": "Senior Spring Boot developer",
        "orm": "Spring Data JPA",
        "patterns_file": "patterns_springboot_java.yaml",
    },
    "laravel": {
        "impl_ext": ".php",
        "language": "PHP",
        "expert_role": "Senior Laravel developer",
        "orm": "Eloquent ORM",
        "patterns_file": "patterns_laravel.yaml",
    },
}


def get_cases_dir(framework: str) -> Path:
    """Get the cases directory for a framework."""
    return Path(__file__).parent.parent / "cases" / framework


# Category mappings
CATEGORY_PREFIXES = {
    "calculation": "CALC",
    "inventory": "STOCK",
    "state": "STATE",
    "authorization": "AUTH",
    "time": "TIME",
    "notification": "NOTIFY",
    "external": "EXT",
    "performance": "PERF",
    "data": "DATA",
    "rails": "RAILS",
    "django": "DJANGO",
    "spring": "SPRING",
    "laravel": "LARAVEL",
    "false_positive": "FP",
}

SPEC_ALIGNMENT_CATEGORIES = [
    "calculation",
    "inventory",
    "state",
    "authorization",
    "time",
    "notification",
]


def parse_patterns_yaml(content: str) -> list[dict[str, Any]]:
    """Parse patterns.yaml without external YAML library."""
    patterns: list[dict[str, Any]] = []
    current: dict[str, Any] = {}

    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            if current:
                patterns.append(current)
                current = {}
            continue

        if line.startswith("- id:"):
            if current:
                patterns.append(current)
            current = {"id": line.split(":", 1)[1].strip()}
        elif line.startswith("  ") and ":" in line and current:
            key, value = line.strip().split(":", 1)
            value = value.strip()
            if value == "null":
                value = None
            elif value.startswith("[") and value.endswith("]"):
                value = [v.strip().strip('"') for v in value[1:-1].split(",") if v.strip()]
            elif value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            current[key] = value

    if current:
        patterns.append(current)

    return patterns


def create_client():
    """Create Anthropic client."""
    global anthropic
    try:
        import anthropic as _anthropic
        anthropic = _anthropic
    except ImportError:
        print("Error: anthropic package not installed. Run: pip install anthropic")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


def generate_with_llm(client: Any, prompt: str, system: str = "") -> str:
    """Call Claude API to generate content."""
    framework_cfg = FRAMEWORK_CONFIG[CONFIG["framework"]]
    default_system = f"You are an expert {framework_cfg['language']} developer specializing in {CONFIG['framework'].title()}."
    message = client.messages.create(
        model=CONFIG["model"],
        max_tokens=MAX_TOKENS,
        temperature=0,
        system=system if system else default_system,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_context_md(client: Any, pattern: dict[str, Any]) -> str:
    """Generate context.md using LLM."""
    category = pattern.get("category", "")
    name = pattern.get("name", "")
    plan = pattern.get("plan", "")
    correct = pattern.get("correct", "")

    framework = CONFIG["framework"]
    framework_cfg = FRAMEWORK_CONFIG[framework]

    if framework == "django":
        prompt = f"""Generate a context.md file for an AI code review benchmark test case.

This file represents the EXISTING CODEBASE that a code reviewer can reference.
It should contain realistic Django/Python code that would exist before the implementation under review.

## Pattern Information
- Category: {category}
- Feature: {name}
- Requirement: {plan}

## Requirements for context.md

1. Start with "# Existing Codebase" heading
2. Include a "## Schema" section with Django model definitions
3. Include a "## Models" section with relevant Django models, managers, and querysets
4. Include useful model methods, custom managers, and constants that SHOULD be used by the implementation
5. The code should hint at the correct approach without explicitly stating it
6. Use realistic Django conventions and patterns (PEP 8, type hints)
7. Keep it focused (100-150 lines max)

## Important
- Do NOT include the implementation under review
- Do NOT include comments like "use this for X" - let the code speak for itself
- Make it look like real production code extracted from a Django app
- Use Python 3.11+ syntax and Django 5.0+ patterns

Generate only the markdown content, no explanations."""
    elif framework == "springboot-java":
        prompt = f"""Generate a context.md file for an AI code review benchmark test case.

This file represents the EXISTING CODEBASE that a code reviewer can reference.
It should contain realistic Spring Boot/Java code that would exist before the implementation under review.

## Pattern Information
- Category: {category}
- Feature: {name}
- Requirement: {plan}

## Requirements for context.md

1. Start with "# Existing Codebase" heading
2. Include a "## Schema" section with JPA entity definitions
3. Include a "## Entities" section with relevant JPA entities and repositories
4. Include useful repository methods, service interfaces, and constants that SHOULD be used by the implementation
5. The code should hint at the correct approach without explicitly stating it
6. Use realistic Spring Boot conventions and patterns
7. Keep it focused (100-150 lines max)

## Important
- Do NOT include the implementation under review
- Do NOT include comments like "use this for X" - let the code speak for itself
- Make it look like real production code extracted from a Spring Boot app
- Use Java 21+ syntax and Spring Boot 3.2+ patterns
- Use BigDecimal for monetary calculations
- Include proper Spring annotations (@Entity, @Repository, @Service, etc.)

Generate only the markdown content, no explanations."""
    elif framework == "laravel":
        prompt = f"""Generate a context.md file for an AI code review benchmark test case.

This file represents the EXISTING CODEBASE that a code reviewer can reference.
It should contain realistic Laravel/PHP code that would exist before the implementation under review.

## Pattern Information
- Category: {category}
- Feature: {name}
- Requirement: {plan}

## Requirements for context.md

1. Start with "# Existing Codebase" heading
2. Include a "## Schema" section with Laravel migration definitions
3. Include a "## Models" section with relevant Eloquent models
4. Include useful scopes, relationships, accessors, and constants that SHOULD be used by the implementation
5. The code should hint at the correct approach without explicitly stating it
6. Use realistic Laravel conventions and patterns
7. Keep it focused (100-150 lines max)

## Important
- Do NOT include the implementation under review
- Do NOT include comments like "use this for X" - let the code speak for itself
- Make it look like real production code extracted from a Laravel app
- Use PHP 8.2+ syntax and Laravel 11+ patterns
- Use proper type hints and return types
- Include proper Laravel conventions (Eloquent, Facades, etc.)

Generate only the markdown content, no explanations."""
    else:
        prompt = f"""Generate a context.md file for an AI code review benchmark test case.

This file represents the EXISTING CODEBASE that a code reviewer can reference.
It should contain realistic Rails code that would exist before the implementation under review.

## Pattern Information
- Category: {category}
- Feature: {name}
- Requirement: {plan}

## Requirements for context.md

1. Start with "# Existing Codebase" heading
2. Include a "## Schema" section with relevant table definitions as Ruby comments
3. Include a "## Models" section with relevant ActiveRecord models
4. Include useful scopes, methods, and constants that SHOULD be used by the implementation
5. The code should hint at the correct approach without explicitly stating it
6. Use realistic Rails conventions and patterns
7. Keep it focused (100-150 lines max)

## Important
- Do NOT include the implementation under review
- Do NOT include comments like "use this for X" - let the code speak for itself
- Make it look like real production code extracted from a Rails app

Generate only the markdown content, no explanations."""

    return generate_with_llm(client, prompt)


def generate_plan_md(client: Any, pattern: dict[str, Any]) -> str:
    """Generate plan.md using LLM."""
    category = pattern.get("category", "")
    name = pattern.get("name", "")
    plan = pattern.get("plan", "")
    is_fp = category == "false_positive"

    framework = CONFIG["framework"]
    framework_names = {"django": "Django", "springboot-java": "Spring Boot (Java)", "rails": "Rails"}
    framework_name = framework_names.get(framework, "Rails")

    prompt = f"""Generate a plan.md file for an AI code review benchmark test case.

This file represents the SPECIFICATION that the code should implement.
A code reviewer will compare the implementation against this plan.

## Pattern Information
- Framework: {framework_name}
- Category: {category}
- Feature: {name.replace('_', ' ').title()}
- Core Requirement: {plan}

## Requirements for plan.md

1. Start with a descriptive title (# heading)
2. Include an "## Overview" section describing the business context
3. Include a "## Requirements" section with numbered, specific requirements
4. Include a "## Constraints" section if applicable (edge cases, validation rules)
5. Include a "## References" section pointing to context.md for existing implementations
6. Be specific enough that a reviewer can verify compliance
7. Do NOT include implementation details or code examples
8. Do NOT include "correct implementation" hints

## Important
- This is what the IMPLEMENTER should have followed
- The reviewer will check if the code matches these requirements
- Keep requirements clear and verifiable
- {"This is a FALSE POSITIVE case - the implementation will be CORRECT" if is_fp else "The implementation will contain a bug related to these requirements"}

Generate only the markdown content, no explanations."""

    return generate_with_llm(client, prompt)


def generate_impl(client: Any, pattern: dict[str, Any], context_content: str = "") -> str:
    """Generate implementation file using LLM (impl.rb for Rails, impl.py for Django, impl.java for Spring Boot).

    Args:
        client: Anthropic client
        pattern: Pattern definition from YAML
        context_content: Content of context.md (used for FP cases to ensure consistency)
    """
    category = pattern.get("category", "")
    name = pattern.get("name", "")
    plan = pattern.get("plan", "")
    bug_description = pattern.get("bug_description", "")
    correct = pattern.get("correct", "")
    incorrect = pattern.get("incorrect", "")
    is_fp = category == "false_positive"

    framework = CONFIG["framework"]

    if framework == "django":
        if is_fp:
            prompt = f"""Generate a Python service class for an AI code review benchmark (Django).

## Pattern Information
- Feature: {name.replace('_', ' ').title()}
- Requirement: {plan}

## Existing Codebase (context.md)
The implementation MUST be consistent with the following existing codebase:

{context_content}

## Requirements

1. Generate a complete, working Python service class (30-80 lines)
2. The implementation should be CORRECT - no bugs
3. Follow Django conventions and PEP 8 best practices
4. Include realistic method structure with private helpers (prefix with _)
5. Use meaningful variable names, type hints, and clear logic flow
6. This is a FALSE POSITIVE test - the code should pass review

## CRITICAL: Consistency with Existing Codebase
- MUST use existing model classes, methods, and fields exactly as defined in context.md
- MUST use existing constants instead of redefining them
- MUST use existing manager/queryset methods instead of creating new ones
- MUST NOT call methods that don't exist in the model definitions
- MUST match the exact method signatures and return types from context.md

## Important
- Do NOT add any comments explaining the code is correct
- Do NOT add TODO or FIXME comments
- Make it look like natural production code
- The code should be reviewable (not too simple, not too complex)

## Output Format
- Output ONLY raw Python code
- Start with appropriate imports (from decimal import Decimal, from django.db import transaction, etc.)
- Do NOT wrap in markdown code blocks (no ```python)
- Do NOT add any explanation before or after the code"""

        else:
            prompt = f"""Generate a Python service class for an AI code review benchmark (Django).

## Pattern Information
- Feature: {name.replace('_', ' ').title()}
- Requirement: {plan}

## Bug to Embed
- Description: {bug_description}
- Incorrect pattern: {incorrect}
- Correct pattern (for reference, do NOT use): {correct}

## Requirements

1. Generate a complete, working Python service class (30-80 lines)
2. The implementation MUST contain the bug described above
3. The bug should be SUBTLE - not obvious at first glance
4. Follow Django conventions and PEP 8 otherwise
5. Include realistic method structure with private helpers (prefix with _)
6. Use meaningful variable names, type hints, and clear logic flow

## Critical Rules
- Do NOT add comments like "# BUG:" or "# TODO:" or "# FIXME:"
- Do NOT add any comments that hint at the bug
- Do NOT add comments explaining what's wrong
- The buggy code should look natural and intentional
- A reviewer should need to carefully read the code to find the bug

## Output Format
- Output ONLY raw Python code
- Start with appropriate imports (from decimal import Decimal, from django.db import transaction, etc.)
- Do NOT wrap in markdown code blocks (no ```python)
- Do NOT add any explanation before or after the code"""

    elif framework == "springboot-java":
        if is_fp:
            prompt = f"""Generate a Java service class for an AI code review benchmark (Spring Boot).

## Pattern Information
- Feature: {name.replace('_', ' ').title()}
- Requirement: {plan}

## Existing Codebase (context.md)
The implementation MUST be consistent with the following existing codebase:

{context_content}

## Requirements

1. Generate a complete, working Java service class (40-100 lines)
2. The implementation should be CORRECT - no bugs
3. Follow Spring Boot conventions and Java best practices
4. Include realistic method structure with private helpers
5. Use meaningful variable names and clear logic flow
6. This is a FALSE POSITIVE test - the code should pass review

## CRITICAL: Consistency with Existing Codebase
- MUST use existing entity classes, methods, and fields exactly as defined in context.md
- MUST use existing constants (e.g., DiscountConstants) instead of redefining them
- MUST use existing repository methods instead of creating new ones
- MUST NOT call methods that don't exist in the entity definitions
- MUST match the exact method signatures and return types from context.md

## Important
- Do NOT add any comments explaining the code is correct
- Do NOT add TODO or FIXME comments
- Make it look like natural production code
- The code should be reviewable (not too simple, not too complex)
- Use BigDecimal for monetary calculations
- Include proper Spring annotations (@Service, @Transactional, etc.)

## Output Format
- Output ONLY raw Java code
- Start with package declaration and imports
- Do NOT wrap in markdown code blocks (no ```java)
- Do NOT add any explanation before or after the code"""

        else:
            prompt = f"""Generate a Java service class for an AI code review benchmark (Spring Boot).

## Pattern Information
- Feature: {name.replace('_', ' ').title()}
- Requirement: {plan}

## Bug to Embed
- Description: {bug_description}
- Incorrect pattern: {incorrect}
- Correct pattern (for reference, do NOT use): {correct}

## Requirements

1. Generate a complete, working Java service class (40-100 lines)
2. The implementation MUST contain the bug described above
3. The bug should be SUBTLE - not obvious at first glance
4. Follow Spring Boot conventions otherwise
5. Include realistic method structure with private helpers
6. Use meaningful variable names and clear logic flow

## Critical Rules
- Do NOT add comments like "// BUG:" or "// TODO:" or "// FIXME:"
- Do NOT add any comments that hint at the bug
- Do NOT add comments explaining what's wrong
- The buggy code should look natural and intentional
- A reviewer should need to carefully read the code to find the bug
- Use BigDecimal for monetary calculations
- Include proper Spring annotations (@Service, @Transactional, etc.)

## Output Format
- Output ONLY raw Java code
- Start with package declaration and imports
- Do NOT wrap in markdown code blocks (no ```java)
- Do NOT add any explanation before or after the code"""

    elif framework == "laravel":
        if is_fp:
            prompt = f"""Generate a PHP service class for an AI code review benchmark (Laravel).

## Pattern Information
- Feature: {name.replace('_', ' ').title()}
- Requirement: {plan}

## Existing Codebase (context.md)
The implementation MUST be consistent with the following existing codebase:

{context_content}

## Requirements

1. Generate a complete, working PHP service class (40-100 lines)
2. The implementation should be CORRECT - no bugs
3. Follow Laravel conventions and PSR-12 best practices
4. Include realistic method structure with private helpers
5. Use meaningful variable names, type hints, and clear logic flow
6. This is a FALSE POSITIVE test - the code should pass review

## CRITICAL: Consistency with Existing Codebase
- MUST use existing model classes, methods, and scopes exactly as defined in context.md
- MUST use existing constants instead of redefining them
- MUST use existing Eloquent relationships and scopes
- MUST NOT call methods that don't exist in the model definitions
- MUST match the exact method signatures from context.md

## Important
- Do NOT add any comments explaining the code is correct
- Do NOT add TODO or FIXME comments
- Make it look like natural production code
- The code should be reviewable (not too simple, not too complex)
- Use proper PHP 8.2+ syntax (constructor promotion, typed properties, etc.)

## Output Format
- Output ONLY raw PHP code
- Start with: <?php
- Include namespace and use statements
- Do NOT wrap in markdown code blocks (no ```php)
- Do NOT add any explanation before or after the code"""

        else:
            prompt = f"""Generate a PHP service class for an AI code review benchmark (Laravel).

## Pattern Information
- Feature: {name.replace('_', ' ').title()}
- Requirement: {plan}

## Bug to Embed
- Description: {bug_description}
- Incorrect pattern: {incorrect}
- Correct pattern (for reference, do NOT use): {correct}

## Requirements

1. Generate a complete, working PHP service class (40-100 lines)
2. The implementation MUST contain the bug described above
3. The bug should be SUBTLE - not obvious at first glance
4. Follow Laravel conventions and PSR-12 otherwise
5. Include realistic method structure with private helpers
6. Use meaningful variable names, type hints, and clear logic flow

## Critical Rules
- Do NOT add comments like "// BUG:" or "// TODO:" or "// FIXME:"
- Do NOT add any comments that hint at the bug
- Do NOT add comments explaining what's wrong
- The buggy code should look natural and intentional
- A reviewer should need to carefully read the code to find the bug
- Use proper PHP 8.2+ syntax (constructor promotion, typed properties, etc.)
- Include proper Laravel patterns (Eloquent, Facades, dependency injection, etc.)

## Output Format
- Output ONLY raw PHP code
- Start with: <?php
- Include namespace and use statements
- Do NOT wrap in markdown code blocks (no ```php)
- Do NOT add any explanation before or after the code"""

    else:  # Rails
        if is_fp:
            prompt = f"""Generate a Ruby service class for an AI code review benchmark.

## Pattern Information
- Feature: {name.replace('_', ' ').title()}
- Requirement: {plan}

## Existing Codebase (context.md)
The implementation MUST be consistent with the following existing codebase:

{context_content}

## Requirements

1. Generate a complete, working Ruby service class (30-80 lines)
2. The implementation should be CORRECT - no bugs
3. Follow Rails conventions and best practices
4. Include realistic method structure with private helpers
5. Use meaningful variable names and clear logic flow
6. This is a FALSE POSITIVE test - the code should pass review

## CRITICAL: Consistency with Existing Codebase
- MUST use existing model classes, methods, and scopes exactly as defined in context.md
- MUST use existing constants instead of redefining them
- MUST use existing model methods instead of creating new ones
- MUST NOT call methods that don't exist in the model definitions
- MUST match the exact method signatures from context.md

## Important
- Do NOT add any comments explaining the code is correct
- Do NOT add TODO or FIXME comments
- Make it look like natural production code
- The code should be reviewable (not too simple, not too complex)

## Output Format
- Output ONLY raw Ruby code
- Start with: # frozen_string_literal: true
- Do NOT wrap in markdown code blocks (no ```ruby)
- Do NOT add any explanation before or after the code"""

        else:
            prompt = f"""Generate a Ruby service class for an AI code review benchmark.

## Pattern Information
- Feature: {name.replace('_', ' ').title()}
- Requirement: {plan}

## Bug to Embed
- Description: {bug_description}
- Incorrect pattern: {incorrect}
- Correct pattern (for reference, do NOT use): {correct}

## Requirements

1. Generate a complete, working Ruby service class (30-80 lines)
2. The implementation MUST contain the bug described above
3. The bug should be SUBTLE - not obvious at first glance
4. Follow Rails conventions otherwise
5. Include realistic method structure with private helpers
6. Use meaningful variable names and clear logic flow

## Critical Rules
- Do NOT add comments like "# BUG:" or "# TODO:" or "# FIXME:"
- Do NOT add any comments that hint at the bug
- Do NOT add comments explaining what's wrong
- The buggy code should look natural and intentional
- A reviewer should need to carefully read the code to find the bug

## Output Format
- Output ONLY raw Ruby code
- Start with: # frozen_string_literal: true
- Do NOT wrap in markdown code blocks (no ```ruby)
- Do NOT add any explanation before or after the code"""

    content = generate_with_llm(client, prompt)

    # Strip markdown code blocks if present
    content = content.strip()
    if content.startswith("```python"):
        content = content[9:]
    elif content.startswith("```ruby"):
        content = content[7:]
    elif content.startswith("```java"):
        content = content[7:]
    elif content.startswith("```php"):
        content = content[6:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]

    return content.strip()


# Keep backward compatibility alias
def generate_impl_rb(client: Any, pattern: dict[str, Any]) -> str:
    """Generate impl.rb using LLM (backward compatibility)."""
    return generate_impl(client, pattern)


def generate_meta_json(pattern: dict[str, Any]) -> dict[str, Any]:
    """Generate meta.json from pattern definition (no LLM needed)."""
    category = pattern.get("category", "")
    is_fp = category == "false_positive"

    axis = None
    if not is_fp:
        axis = "spec_alignment" if category in SPEC_ALIGNMENT_CATEGORIES else "implicit_knowledge"

    framework = CONFIG["framework"]
    framework_cfg = FRAMEWORK_CONFIG[framework]

    meta = {
        "case_id": pattern.get("id", ""),
        "category": category,
        "axis": axis,
        "name": pattern.get("name", ""),
        "difficulty": pattern.get("difficulty", "medium"),
        "expected_detection": not is_fp,
        "bug_description": pattern.get("bug_description") if not is_fp else None,
        "bug_anchor": pattern.get("incorrect") if not is_fp else None,
        "correct_implementation": pattern.get("correct"),
        "severity": pattern.get("severity") if not is_fp else None,
        "tags": pattern.get("tags", []),
    }

    # Add framework-specific fields
    if framework == "django":
        meta["framework"] = "django"
        meta["framework_version"] = "5.0+"
        meta["python_version"] = "3.11+"
    elif framework == "springboot-java":
        meta["framework"] = "springboot-java"
        meta["framework_version"] = "3.2+"
        meta["java_version"] = "21+"
    elif framework == "laravel":
        meta["framework"] = "laravel"
        meta["framework_version"] = "11+"
        meta["php_version"] = "8.2+"

    return meta


def verify_bug_anchor(impl_content: str, bug_anchor: str | None) -> bool:
    """Verify that the bug anchor exists in the implementation.

    Uses flexible matching: extracts key operators/literals from bug_anchor
    and checks if they appear in the implementation.
    """
    if bug_anchor is None:
        return True  # FP cases don't have bug anchors

    # Normalize whitespace for comparison
    normalized_impl = " ".join(impl_content.split())
    normalized_anchor = " ".join(bug_anchor.split())

    # Exact match
    if normalized_anchor in normalized_impl:
        return True

    # Flexible match: extract key patterns (numbers, operators, method calls)
    # Examples: "* 0.1" -> check for "* 0.1" or "*0.1" or "* 0.10"
    import re

    # Extract numeric literals and operators
    key_patterns = []

    # Look for multiplication/division with decimals (common in calculation bugs)
    decimal_ops = re.findall(r'[*/]\s*\d+\.?\d*', bug_anchor)
    key_patterns.extend(decimal_ops)

    # Look for comparison operators (common in boundary bugs)
    comparisons = re.findall(r'[<>=!]+\s*\d+', bug_anchor)
    key_patterns.extend(comparisons)

    # Look for method calls
    method_calls = re.findall(r'\.\w+', bug_anchor)
    key_patterns.extend(method_calls)

    # If we found key patterns, check if any appear in the impl
    if key_patterns:
        normalized_impl_no_space = impl_content.replace(" ", "")
        for pattern in key_patterns:
            pattern_no_space = pattern.replace(" ", "")
            if pattern_no_space in normalized_impl_no_space:
                return True

    return False


def generate_case(
    client: Any,
    pattern: dict[str, Any],
    output_dir: Path,
    max_retries: int = 3,
) -> tuple[Path, bool]:
    """Generate a complete test case using LLM."""
    case_id = pattern.get("id", "UNKNOWN")
    case_dir = output_dir / case_id
    case_dir.mkdir(parents=True, exist_ok=True)

    framework = CONFIG["framework"]
    framework_cfg = FRAMEWORK_CONFIG[framework]
    impl_filename = f"impl{framework_cfg['impl_ext']}"

    print(f"  Generating context.md...")
    context_content = generate_context_md(client, pattern)
    (case_dir / "context.md").write_text(context_content, encoding="utf-8")

    print(f"  Generating plan.md...")
    plan_content = generate_plan_md(client, pattern)
    (case_dir / "plan.md").write_text(plan_content, encoding="utf-8")

    # Generate impl file with retry for bug anchor verification
    bug_anchor = pattern.get("incorrect")
    is_fp = pattern.get("category") == "false_positive"

    for attempt in range(max_retries):
        print(f"  Generating {impl_filename} (attempt {attempt + 1}/{max_retries})...")
        # Pass context_content to generate_impl for FP cases to ensure consistency
        impl_content = generate_impl(client, pattern, context_content if is_fp else "")

        if is_fp or verify_bug_anchor(impl_content, bug_anchor):
            (case_dir / impl_filename).write_text(impl_content, encoding="utf-8")
            break
        else:
            print(f"    Warning: Bug anchor not found, retrying...")
    else:
        # Save anyway but flag the issue
        (case_dir / impl_filename).write_text(impl_content, encoding="utf-8")
        print(f"    ERROR: Bug anchor '{bug_anchor}' not found after {max_retries} attempts")

    print(f"  Generating meta.json...")
    meta = generate_meta_json(pattern)
    meta["bug_anchor_verified"] = is_fp or verify_bug_anchor(impl_content, bug_anchor)

    with open(case_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # Rate limiting
    time.sleep(0.5)

    return case_dir, meta["bug_anchor_verified"]


def estimate_cost(num_cases: int) -> dict[str, float]:
    """Estimate API cost for generating cases."""
    # Rough estimates per case
    input_tokens_per_case = 2000  # prompts
    output_tokens_per_case = 3000  # context + plan + impl

    total_input = input_tokens_per_case * num_cases * 3  # 3 calls per case
    total_output = output_tokens_per_case * num_cases

    input_cost = (total_input / 1_000_000) * INPUT_PRICE
    output_cost = (total_output / 1_000_000) * OUTPUT_PRICE

    return {
        "input_tokens": total_input,
        "output_tokens": total_output,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": input_cost + output_cost,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate test cases using Claude API")
    parser.add_argument("--pattern", help="Generate specific pattern (e.g., CALC_001)")
    parser.add_argument("--category", help="Generate all patterns in category")
    parser.add_argument("--all", action="store_true", help="Generate all patterns")
    parser.add_argument("--dry-run", action="store_true", help="Show cost estimate only")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model to use (default: {DEFAULT_MODEL})")
    parser.add_argument(
        "--framework",
        choices=["rails", "django", "springboot-java", "laravel"],
        default="rails",
        help="Target framework (default: rails)",
    )
    parser.add_argument(
        "--output",
        help="Output directory (default: cases/{framework})",
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt",
    )
    args = parser.parse_args()

    CONFIG["model"] = args.model
    CONFIG["framework"] = args.framework

    framework_cfg = FRAMEWORK_CONFIG[args.framework]
    patterns_file = Path(__file__).parent.parent / framework_cfg["patterns_file"]

    if not patterns_file.exists():
        print(f"Error: Patterns file not found: {patterns_file}")
        sys.exit(1)

    with open(patterns_file, encoding="utf-8") as f:
        patterns = parse_patterns_yaml(f.read())

    # Filter patterns based on arguments
    if args.pattern:
        patterns = [p for p in patterns if p.get("id") == args.pattern]
        if not patterns:
            print(f"Pattern not found: {args.pattern}")
            sys.exit(1)
    elif args.category:
        patterns = [p for p in patterns if p.get("category") == args.category]
        if not patterns:
            print(f"No patterns found for category: {args.category}")
            sys.exit(1)
    elif not args.all:
        parser.print_help()
        sys.exit(0)

    # Determine output directory
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = get_cases_dir(args.framework)

    # Cost estimate
    estimate = estimate_cost(len(patterns))
    print(f"\n{'=' * 60}")
    print(f"Test Case Generation Plan")
    print(f"{'=' * 60}")
    print(f"Framework: {args.framework}")
    print(f"Model: {CONFIG['model']}")
    print(f"Cases to generate: {len(patterns)}")
    print(f"Output directory: {output_dir}")
    print(f"Estimated tokens: {estimate['input_tokens']:,} input, {estimate['output_tokens']:,} output")
    print(f"Estimated cost: ${estimate['total_cost']:.2f}")
    print(f"{'=' * 60}\n")

    if args.dry_run:
        print("Dry run - no cases generated")
        return

    # Confirm before proceeding
    if not args.yes:
        response = input("Proceed with generation? [y/N]: ")
        if response.lower() != "y":
            print("Cancelled")
            return

    # Generate cases
    client = create_client()

    generated = 0
    verified = 0
    failed_verifications = []

    for i, pattern in enumerate(patterns, 1):
        case_id = pattern.get("id", "UNKNOWN")
        print(f"\n[{i}/{len(patterns)}] Generating {case_id}...")

        try:
            case_dir, anchor_verified = generate_case(client, pattern, output_dir)
            generated += 1
            if anchor_verified:
                verified += 1
            else:
                failed_verifications.append(case_id)
            print(f"  Done: {case_dir}")
        except Exception as e:
            print(f"  ERROR: {e}")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Generation Complete")
    print(f"{'=' * 60}")
    print(f"Generated: {generated}/{len(patterns)} cases")
    print(f"Bug anchor verified: {verified}/{generated}")

    if failed_verifications:
        print(f"\nCases requiring manual review (bug anchor not found):")
        for case_id in failed_verifications:
            print(f"  - {case_id}")


if __name__ == "__main__":
    main()