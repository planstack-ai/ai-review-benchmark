#!/usr/bin/env python3
"""
Migrate test cases to dual-mode evaluation structure.

This script:
1. Splits existing context.md into context_base.md and context_guidelines.md
2. Updates meta.json with dual_config and fix_validation fields
3. Generates context.md from the split files for backward compatibility

Usage:
    python scripts/migrate_to_dual.py --dry-run  # Preview changes
    python scripts/migrate_to_dual.py            # Apply changes
    python scripts/migrate_to_dual.py --case RAILS_001  # Single case
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any


CASES_DIR = Path(__file__).parent.parent / "cases" / "rails"

# Categories that should use dual mode (Implicit Knowledge axis)
DUAL_MODE_CATEGORIES = {"rails", "perf", "data", "ext"}

# Patterns to identify guidelines sections
GUIDELINES_PATTERNS = [
    r"^## Usage Guidelines.*?(?=^## |\Z)",
    r"^## Notes.*?(?=^## |\Z)",
    r"^## Best Practices.*?(?=^## |\Z)",
    r"^## Guidelines.*?(?=^## |\Z)",
    r"^## Conventions.*?(?=^## |\Z)",
]

# Template for generating guidelines when none exist
GUIDELINES_TEMPLATE = """## Usage Guidelines

{guidelines_content}
"""


def extract_guidelines_section(content: str) -> tuple[str, str]:
    """Extract guidelines section from context.md content.

    Returns:
        Tuple of (base_content, guidelines_content).
        If no guidelines found, guidelines_content is empty string.
    """
    for pattern in GUIDELINES_PATTERNS:
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            guidelines = match.group(0).strip()
            base = content[:match.start()] + content[match.end():]
            base = base.strip()
            return base, guidelines

    return content.strip(), ""


def generate_guidelines_from_meta(meta: dict[str, Any]) -> str:
    """Generate guidelines content from meta.json information.

    This creates appropriate guidelines based on the bug being tested,
    which can be used for the "explicit" evaluation mode.

    IMPORTANT: Guidelines should describe PRINCIPLES, not give away the exact solution.
    They should be like what a senior engineer would write in a style guide.
    """
    category = meta.get("category", "")
    bug_description = meta.get("bug_description", "")
    tags = meta.get("tags", [])
    name = meta.get("name", "")

    guidelines_parts = []

    # Generate guidelines based on category - focus on principles, not solutions
    if category == "rails":
        if "scope" in tags:
            guidelines_parts.append(
                "Use existing model scopes instead of writing raw `where` clauses. "
                "This ensures consistent behavior and better maintainability. "
                "Check the model definition for available scopes before writing queries."
            )
        if "association" in tags or "dependent" in tags:
            guidelines_parts.append(
                "All `has_many` associations should specify a `dependent` option "
                "(`:destroy`, `:delete_all`, `:nullify`, etc.) to handle child records "
                "when the parent is deleted. Failing to do so can leave orphaned records."
            )
        if "enum" in tags:
            guidelines_parts.append(
                "Use Rails enum for status fields instead of string comparisons. "
                "This provides type safety, convenient query methods, and prevents typos."
            )
        if "callback" in tags:
            guidelines_parts.append(
                "Be mindful of callback execution order. Callbacks in the same phase "
                "execute in the order they are defined. Ensure proper sequencing of operations."
            )
        if "transaction" in tags:
            guidelines_parts.append(
                "Wrap related database operations in transactions to ensure atomicity. "
                "Use `requires_new: true` for nested transactions when inner operations "
                "should have independent commit/rollback behavior."
            )
        if "strong_parameters" in name or "strong_param" in name:
            guidelines_parts.append(
                "Always use strong parameters to whitelist permitted attributes. "
                "Never allow mass assignment of sensitive fields like role, admin, etc."
            )
        if "find_or_create" in name or "race" in tags:
            guidelines_parts.append(
                "Use database constraints (unique indexes) in addition to ActiveRecord "
                "validations to prevent race conditions when creating records."
            )
        if "update_all" in name or "callback" in name:
            guidelines_parts.append(
                "Be aware that `update_all` and `delete_all` skip callbacks and validations. "
                "Use them only when you intentionally want to bypass model logic."
            )
        if "job" in name or "after_commit" in name:
            guidelines_parts.append(
                "Background jobs should be enqueued in `after_commit` callbacks, not "
                "`after_save`, to ensure the transaction has committed before the job runs."
            )

    elif category in ("perf", "performance"):
        if "n+1" in bug_description.lower() or "n_plus" in name:
            guidelines_parts.append(
                "Use `includes`, `preload`, or `eager_load` to avoid N+1 queries when "
                "iterating over collections and accessing associations. "
                "Prefer `includes` for most cases."
            )
        if "count" in bug_description.lower() or "length" in name or "inefficient" in name:
            guidelines_parts.append(
                "Use `count` for database COUNT queries. Avoid `length` or `size` on "
                "ActiveRecord relations as they load all records into memory."
            )
        if "full" in name or "all" in bug_description.lower():
            guidelines_parts.append(
                "Never load entire tables into memory. Use `find_each` or `find_in_batches` "
                "for batch processing large datasets."
            )
        if "eager" in name or "unnecessary" in name:
            guidelines_parts.append(
                "Only eager load associations that will actually be used. "
                "Unnecessary eager loading can slow down queries."
            )
        if "cache" in name:
            guidelines_parts.append(
                "Design cache keys carefully. Include all variables that affect the cached "
                "content (user_id, locale, etc.) to prevent showing wrong data."
            )
        if "index" in name:
            guidelines_parts.append(
                "Ensure database indexes exist for columns used in WHERE clauses, "
                "ORDER BY, and JOIN conditions for optimal query performance."
            )

    elif category == "data":
        if "foreign" in bug_description.lower() or "constraint" in name:
            guidelines_parts.append(
                "Add database-level foreign key constraints in addition to ActiveRecord "
                "associations to ensure referential integrity."
            )
        if "unique" in bug_description.lower() or "constraint" in name:
            guidelines_parts.append(
                "Add unique indexes at the database level in addition to uniqueness "
                "validations to prevent race condition duplicates."
            )
        if "lock" in bug_description.lower() or "optimistic" in name or "concurrent" in name:
            guidelines_parts.append(
                "Use optimistic locking (`lock_version` column) or pessimistic locking "
                "(`lock!`) for records that may be updated concurrently."
            )
        if "soft_delete" in name or "deleted" in bug_description.lower():
            guidelines_parts.append(
                "When using soft deletes, ensure all queries properly filter out deleted "
                "records. Consider using default scopes or the `paranoia` gem."
            )
        if "history" in name or "master" in bug_description.lower():
            guidelines_parts.append(
                "Store snapshots of master data (prices, names, etc.) at transaction time. "
                "Don't rely on current master data values for historical records."
            )
        if "default" in name or "null" in bug_description.lower():
            guidelines_parts.append(
                "When adding new columns, consider the default value carefully. "
                "NULL can cause unexpected behavior in queries and calculations."
            )

    elif category == "external" or category == "ext":
        if "timeout" in bug_description.lower():
            guidelines_parts.append(
                "Always handle timeouts when calling external APIs. Consider what state "
                "the system should be in when we don't know if the external call succeeded. "
                "Implement monitoring and manual recovery procedures."
            )
        if "idempotent" in bug_description.lower() or "webhook" in name:
            guidelines_parts.append(
                "Webhook handlers must be idempotent - calling them multiple times with "
                "the same payload should have the same effect as calling once. "
                "Use idempotency keys or check for existing records."
            )
        if "transaction" in bug_description.lower() or "rollback" in bug_description.lower():
            guidelines_parts.append(
                "Never call external APIs inside database transactions. "
                "The transaction may rollback but the external call cannot be undone. "
                "Separate the transaction from external calls."
            )
        if "retry" in name or "duplicate" in bug_description.lower():
            guidelines_parts.append(
                "Implement idempotency for operations that may be retried. "
                "Network errors can cause duplicate requests even when the first succeeded."
            )
        if "sync" in name or "delay" in bug_description.lower():
            guidelines_parts.append(
                "Account for synchronization delays with external systems. "
                "Data may not be immediately consistent across services."
            )

    # If no specific guidelines matched, add category-generic guidelines
    if not guidelines_parts:
        if category in ("rails", "perf", "data", "external", "ext"):
            guidelines_parts.append(
                "Follow Rails best practices and conventions. "
                "Review existing code patterns in the codebase for consistency."
            )

    return "\n\n".join(f"- {part}" for part in guidelines_parts)


def create_fix_validation(meta: dict[str, Any]) -> dict[str, Any]:
    """Create fix_validation config from meta.json."""
    correct_impl = meta.get("correct_implementation", "")
    bug_anchor = meta.get("bug_anchor", "")

    fix_validation = {
        "must_contain": [],
        "must_not_contain": []
    }

    if correct_impl:
        # Extract key patterns from correct implementation
        fix_validation["must_contain"].append(correct_impl)

    if bug_anchor:
        # The bug anchor is what should NOT be in the fix
        fix_validation["must_not_contain"].append(bug_anchor)

    return fix_validation


def process_case(case_dir: Path, dry_run: bool = False, force_regenerate: bool = False) -> dict[str, Any]:
    """Process a single test case directory.

    Args:
        case_dir: Path to case directory
        dry_run: If True, don't write any files
        force_regenerate: If True, regenerate auto-generated guidelines

    Returns:
        Dict with processing results
    """
    result = {
        "case_id": case_dir.name,
        "status": "skipped",
        "changes": []
    }

    meta_file = case_dir / "meta.json"
    context_file = case_dir / "context.md"
    context_base_file = case_dir / "context_base.md"

    if not meta_file.exists():
        result["status"] = "error"
        result["error"] = "meta.json not found"
        return result

    if not context_file.exists():
        result["status"] = "error"
        result["error"] = "context.md not found"
        return result

    # Load meta
    meta = json.loads(meta_file.read_text())
    category = meta.get("category", "")
    axis = meta.get("axis", "")

    # Only process Implicit Knowledge axis cases
    if axis != "implicit_knowledge":
        result["status"] = "skipped"
        result["reason"] = f"Not implicit_knowledge axis (axis={axis})"
        return result

    # Check if we should regenerate auto-generated guidelines
    was_auto_generated = meta.get("dual_config", {}).get("guidelines_generated", False)

    # Also detect old-style auto-generated guidelines that have "The correct approach is:"
    context_guidelines_file_check = case_dir / "context_guidelines.md"
    if context_guidelines_file_check.exists():
        current_guidelines = context_guidelines_file_check.read_text()
        if "The correct approach is:" in current_guidelines:
            was_auto_generated = True  # These need to be regenerated

    # Read base content - prefer context_base.md if it exists (from previous run)
    if context_base_file.exists() and was_auto_generated and force_regenerate:
        # Use existing base file when regenerating
        base_content = context_base_file.read_text().strip()
        guidelines_content = ""  # Will be regenerated
    else:
        # Read current context and split
        context_content = context_file.read_text()
        base_content, guidelines_content = extract_guidelines_section(context_content)

    # Generate guidelines if none found OR if regenerating auto-generated ones
    guidelines_generated = False
    if not guidelines_content or (was_auto_generated and force_regenerate):
        generated_guidelines = generate_guidelines_from_meta(meta)
        guidelines_content = GUIDELINES_TEMPLATE.format(
            guidelines_content=generated_guidelines
        )
        guidelines_generated = True
        if force_regenerate and was_auto_generated:
            result["changes"].append("Regenerated auto-generated guidelines")

    # Prepare file contents
    context_base_file = case_dir / "context_base.md"
    context_guidelines_file = case_dir / "context_guidelines.md"

    # Update meta.json
    updated_meta = meta.copy()
    updated_meta["evaluation_mode"] = "dual"
    updated_meta["dual_config"] = {
        "explicit_includes_guidelines": True,
        "implicit_requires_inference": True,
        "guidelines_generated": guidelines_generated
    }
    updated_meta["fix_required"] = True
    updated_meta["fix_validation"] = create_fix_validation(meta)

    result["changes"] = [
        f"Create context_base.md ({len(base_content)} chars)",
        f"Create context_guidelines.md ({len(guidelines_content)} chars)",
        f"Update meta.json (evaluation_mode=dual)",
    ]
    if guidelines_generated:
        result["changes"].append("Guidelines auto-generated from meta.json")

    if not dry_run:
        # Write files
        context_base_file.write_text(base_content + "\n")
        context_guidelines_file.write_text(guidelines_content + "\n")

        # Regenerate context.md (base + guidelines)
        combined_content = base_content + "\n\n" + guidelines_content
        context_file.write_text(combined_content + "\n")

        # Update meta.json
        meta_file.write_text(
            json.dumps(updated_meta, indent=2, ensure_ascii=False) + "\n"
        )

    result["status"] = "processed"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate test cases to dual-mode evaluation structure"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files"
    )
    parser.add_argument(
        "--case",
        type=str,
        help="Process only a specific case (e.g., RAILS_001)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--force-regenerate",
        action="store_true",
        help="Regenerate auto-generated guidelines with improved logic"
    )

    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN MODE - No files will be modified\n")

    if args.force_regenerate:
        print("FORCE REGENERATE MODE - Regenerating auto-generated guidelines\n")

    # Find cases to process
    if args.case:
        case_dirs = [CASES_DIR / args.case]
        if not case_dirs[0].exists():
            print(f"Error: Case not found: {args.case}")
            return
    else:
        case_dirs = sorted([d for d in CASES_DIR.iterdir() if d.is_dir()])

    # Process cases
    results = {
        "processed": [],
        "skipped": [],
        "errors": []
    }

    for case_dir in case_dirs:
        result = process_case(case_dir, dry_run=args.dry_run, force_regenerate=args.force_regenerate)

        if result["status"] == "processed":
            results["processed"].append(result)
            print(f"✓ {result['case_id']}")
            if args.verbose:
                for change in result["changes"]:
                    print(f"    - {change}")
        elif result["status"] == "skipped":
            results["skipped"].append(result)
            if args.verbose:
                reason = result.get("reason", "Unknown")
                print(f"○ {result['case_id']} (skipped: {reason})")
        else:
            results["errors"].append(result)
            print(f"✗ {result['case_id']}: {result.get('error', 'Unknown error')}")

    # Summary
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Processed: {len(results['processed'])}")
    print(f"  Skipped:   {len(results['skipped'])}")
    print(f"  Errors:    {len(results['errors'])}")

    if args.dry_run:
        print(f"\nRun without --dry-run to apply changes")


if __name__ == "__main__":
    main()
