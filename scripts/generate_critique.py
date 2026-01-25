#!/usr/bin/env python3
"""
Generate expected_critique.md files for benchmark test cases.

This script generates initial drafts of expected_critique.md files
from meta.json data. It can optionally use an LLM to generate more
detailed critiques.

Usage:
    # Generate critique for a single case
    python scripts/generate_critique.py --case CALC_001

    # Generate critiques for all cases
    python scripts/generate_critique.py --all

    # Generate critiques using LLM for enhanced content
    python scripts/generate_critique.py --all --use-llm

    # Preview without writing files
    python scripts/generate_critique.py --case CALC_001 --dry-run
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

try:
    import anthropic
except ImportError:
    anthropic = None


CASES_DIR = Path(__file__).parent.parent / "cases" / "rails"

# Template for bug cases (expected_detection=true)
BUG_CASE_TEMPLATE = """# Expected Critique for {case_id}

## Essential Finding

{essential_finding}

## Key Points to Mention

{key_points}

## Severity Rationale

This is a **{severity}** issue because:
{severity_rationale}

## Acceptable Variations

{acceptable_variations}

## What Should NOT Be Flagged

- Minor code style issues unrelated to the bug
- Optimization suggestions that don't affect correctness
"""

# Template for false positive cases (expected_detection=false)
FP_CASE_TEMPLATE = """# Expected Critique for {case_id}

## Expected Behavior

This code is correct and should NOT be flagged as problematic.
{description}

## What Makes This Code Correct

{correct_aspects}

## Acceptable Feedback

The AI reviewer may provide:
- Minor style suggestions (acceptable)
- Performance optimization ideas (acceptable if not flagged as bugs)
- Documentation improvements (acceptable)

## What Should NOT Be Flagged

{should_not_flag}

## False Positive Triggers

Watch out for these common false positive patterns:
{fp_triggers}
"""

# LLM prompt for generating enhanced bug case critiques
LLM_BUG_CRITIQUE_PROMPT = """You are helping create ground truth for an AI code review benchmark.

Generate an expected_critique.md file for evaluating AI code reviewers.

## Case Information
- Case ID: {case_id}
- Category: {category}
- Bug Description: {bug_description}
- Bug Location (code anchor): {bug_anchor}
- Correct Implementation: {correct_implementation}
- Severity: {severity}
- Difficulty: {difficulty}

## Plan/Specification
{plan_content}

## Code Under Review
```ruby
{impl_content}
```

## Your Task

Generate the content for expected_critique.md following this structure:

1. **Essential Finding**: 2-3 sentences describing the core issue that MUST be identified. Be specific about the exact bug and its impact.

2. **Key Points to Mention**: 3-5 numbered points that a thorough review should cover:
   - The specific code location
   - Why the current implementation is wrong
   - The correct fix
   - Business/technical impact

3. **Severity Rationale**: 2-3 bullet points explaining why this is {severity} severity. Focus on:
   - Business impact
   - Scope of affected functionality
   - Potential consequences

4. **Acceptable Variations**: 2-3 bullet points describing alternative correct ways to describe this bug. Different phrasings or approaches that would still be correct.

Return ONLY the markdown content for the critique file, starting with "# Expected Critique".
"""

# LLM prompt for generating enhanced FP case critiques
LLM_FP_CRITIQUE_PROMPT = """You are helping create ground truth for an AI code review benchmark.

Generate an expected_critique.md file for a FALSE POSITIVE test case - code that is correct and should NOT be flagged as having bugs.

## Case Information
- Case ID: {case_id}
- Category: false_positive
- Description: {description}
- Tags: {tags}
- Difficulty: {difficulty}

## Plan/Specification
{plan_content}

## Code Under Review (This code is CORRECT)
```ruby
{impl_content}
```

## Your Task

Generate the content for expected_critique.md following this structure:

1. **Expected Behavior**: 2-3 sentences explaining that this code is correct and why.

2. **What Makes This Code Correct**: 3-4 bullet points explaining the aspects that make this implementation correct:
   - Proper patterns used
   - Correct business logic
   - Appropriate error handling

3. **Acceptable Feedback**: What minor suggestions are OK (style, docs) vs. what would be false positives (incorrectly flagging bugs).

4. **What Should NOT Be Flagged**: 3-4 specific things that might look like bugs but aren't.

5. **False Positive Triggers**: 2-3 patterns that commonly trigger false positives in AI reviewers.

Return ONLY the markdown content for the critique file, starting with "# Expected Critique".
"""


def load_case_files(case_dir: Path) -> dict[str, Any]:
    """Load all files for a test case."""
    meta_path = case_dir / "meta.json"
    plan_path = case_dir / "plan.md"
    impl_path = case_dir / "impl.rb"

    if not meta_path.exists():
        return None

    result = {
        "meta": json.loads(meta_path.read_text()),
        "plan": plan_path.read_text() if plan_path.exists() else "",
        "impl": impl_path.read_text() if impl_path.exists() else "",
    }

    return result


def generate_simple_bug_critique(meta: dict[str, Any]) -> str:
    """Generate a simple critique for bug cases from meta.json only."""
    case_id = meta["case_id"]
    bug_description = meta.get("bug_description", "Bug not described")
    bug_anchor = meta.get("bug_anchor", "N/A")
    correct_impl = meta.get("correct_implementation", "N/A")
    severity = meta.get("severity", "medium")
    category = meta.get("category", "unknown")

    essential_finding = f"The code contains a bug: {bug_description}. The problematic code is: `{bug_anchor}`."

    key_points = f"""1. The code `{bug_anchor}` is incorrect
2. The correct implementation should be: `{correct_impl}`
3. This affects the {category} functionality
4. The bug would cause incorrect behavior in production"""

    severity_rationale = f"""- This is a {severity} severity issue based on its impact
- The bug affects core functionality in the {category} domain
- Users or business operations could be directly impacted"""

    acceptable_variations = """- Different wording to describe the same fundamental issue
- Focusing on the symptom vs. the root cause (both acceptable)
- Technical vs. business-impact focused descriptions"""

    return BUG_CASE_TEMPLATE.format(
        case_id=case_id,
        essential_finding=essential_finding,
        key_points=key_points,
        severity=severity,
        severity_rationale=severity_rationale,
        acceptable_variations=acceptable_variations,
    )


def generate_simple_fp_critique(meta: dict[str, Any]) -> str:
    """Generate a simple critique for false positive cases."""
    case_id = meta["case_id"]
    correct_impl = meta.get("correct_implementation", "Standard implementation")
    tags = meta.get("tags", [])
    name = meta.get("name", "unknown")

    description = f"This is a {name} implementation. {correct_impl}."

    correct_aspects = """- Follows standard Rails/Ruby conventions
- Implements the specification correctly
- Has appropriate error handling
- Uses proper patterns for this type of functionality"""

    should_not_flag = """- The implementation follows the specification exactly
- Any patterns that look unusual but are intentional
- Code that might seem redundant but serves a purpose"""

    fp_triggers = """- Pattern matching that looks similar to common bug patterns
- Unconventional but correct approaches
- Code that appears to have missing validation (but is intentionally minimal)"""

    return FP_CASE_TEMPLATE.format(
        case_id=case_id,
        description=description,
        correct_aspects=correct_aspects,
        should_not_flag=should_not_flag,
        fp_triggers=fp_triggers,
    )


def generate_llm_critique(
    case_data: dict[str, Any],
    client: "anthropic.Anthropic",
) -> str:
    """Generate an enhanced critique using LLM."""
    meta = case_data["meta"]
    plan_content = case_data["plan"]
    impl_content = case_data["impl"]

    expected_detection = meta.get("expected_detection", True)

    if expected_detection:
        prompt = LLM_BUG_CRITIQUE_PROMPT.format(
            case_id=meta["case_id"],
            category=meta.get("category", "unknown"),
            bug_description=meta.get("bug_description", "N/A"),
            bug_anchor=meta.get("bug_anchor", "N/A"),
            correct_implementation=meta.get("correct_implementation", "N/A"),
            severity=meta.get("severity", "medium"),
            difficulty=meta.get("difficulty", "medium"),
            plan_content=plan_content,
            impl_content=impl_content,
        )
    else:
        prompt = LLM_FP_CRITIQUE_PROMPT.format(
            case_id=meta["case_id"],
            description=meta.get("correct_implementation", "Standard implementation"),
            tags=", ".join(meta.get("tags", [])),
            difficulty=meta.get("difficulty", "medium"),
            plan_content=plan_content,
            impl_content=impl_content,
        )

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def process_case(
    case_dir: Path,
    use_llm: bool = False,
    client: "anthropic.Anthropic | None" = None,
    dry_run: bool = False,
    force: bool = False,
) -> bool:
    """Process a single test case and generate expected_critique.md."""
    critique_path = case_dir / "expected_critique.md"

    if critique_path.exists() and not force:
        print(f"  SKIP: {case_dir.name} (already exists, use --force to overwrite)")
        return False

    case_data = load_case_files(case_dir)
    if case_data is None:
        print(f"  ERROR: {case_dir.name} (no meta.json found)")
        return False

    meta = case_data["meta"]
    expected_detection = meta.get("expected_detection", True)

    # Generate critique
    if use_llm and client:
        print(f"  Generating with LLM: {case_dir.name}...", end=" ", flush=True)
        try:
            critique = generate_llm_critique(case_data, client)
            print("done")
        except Exception as e:
            print(f"error: {e}")
            # Fall back to simple generation
            if expected_detection:
                critique = generate_simple_bug_critique(meta)
            else:
                critique = generate_simple_fp_critique(meta)
    else:
        if expected_detection:
            critique = generate_simple_bug_critique(meta)
        else:
            critique = generate_simple_fp_critique(meta)
        print(f"  Generated: {case_dir.name}")

    if dry_run:
        print(f"\n--- Preview for {case_dir.name} ---")
        print(critique[:500] + "..." if len(critique) > 500 else critique)
        print("---\n")
    else:
        critique_path.write_text(critique)
        print(f"  Wrote: {critique_path}")

        # Update meta.json to add evaluation_mode and has_expected_critique
        meta_path = case_dir / "meta.json"
        meta["evaluation_mode"] = "semantic"
        meta["has_expected_critique"] = True
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
        print(f"  Updated: {meta_path}")

    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate expected_critique.md files for benchmark test cases"
    )
    parser.add_argument(
        "--case",
        type=str,
        help="Case ID to process (e.g., CALC_001)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all cases",
    )
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Use LLM to generate enhanced critiques",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without writing files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing expected_critique.md files",
    )

    args = parser.parse_args()

    if not args.case and not args.all:
        print("Error: Must specify --case CASE_ID or --all", file=sys.stderr)
        sys.exit(1)

    # Initialize LLM client if needed
    client = None
    if args.use_llm:
        if anthropic is None:
            print("Error: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
            sys.exit(1)
        client = anthropic.Anthropic()

    # Find and process cases
    processed = 0
    skipped = 0

    if args.case:
        # Process single case
        case_dirs = list(CASES_DIR.glob(f"*{args.case}*"))
        if not case_dirs:
            print(f"Error: Case not found: {args.case}", file=sys.stderr)
            sys.exit(1)
    else:
        # Process all cases
        case_dirs = sorted([d for d in CASES_DIR.iterdir() if d.is_dir()])

    print(f"Processing {len(case_dirs)} case(s)...\n")

    for case_dir in case_dirs:
        if process_case(case_dir, args.use_llm, client, args.dry_run, args.force):
            processed += 1
        else:
            skipped += 1

    print(f"\nDone: {processed} processed, {skipped} skipped")


if __name__ == "__main__":
    main()
