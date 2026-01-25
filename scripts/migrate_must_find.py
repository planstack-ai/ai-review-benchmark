#!/usr/bin/env python3
"""
Migration script to add must_find field to meta.json files.

Generates must_find entries based on existing bug_description, bug_anchor,
and expected_critique.md content.

Usage:
    # Preview changes (dry-run)
    python scripts/migrate_must_find.py --dry-run

    # Migrate specific case
    python scripts/migrate_must_find.py --case CALC_001

    # Migrate all cases
    python scripts/migrate_must_find.py --all

    # Use LLM to generate better must_find entries
    python scripts/migrate_must_find.py --all --use-llm
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass


CASES_DIR = Path(__file__).parent.parent / "cases" / "rails"

# Category mapping from existing categories to extractor categories
CATEGORY_MAP = {
    "calculation": "calculation_error",
    "authorization": "authorization",
    "state": "state_management",
    "stock": "data_integrity",
    "time": "time_handling",
    "notification": "notification",
    "external": "external_api",
    "performance": "performance",
    "data": "data_integrity",
    "rails": "logic_error",
    "false_positive": None,  # No must_find for FP cases
}


def extract_keywords_from_text(text: str, min_length: int = 2) -> list[str]:
    """Extract potential keywords from text.

    Args:
        text: Text to extract keywords from
        min_length: Minimum keyword length

    Returns:
        List of keywords
    """
    if not text:
        return []

    # Find code-like patterns (with dots, underscores, operators)
    code_patterns = re.findall(r'[\w_]+(?:\.[\w_]+)*(?:\([^)]*\))?', text)

    # Find quoted strings
    quoted = re.findall(r'["\']([^"\']+)["\']', text)

    # Find numbers and operators
    numbers = re.findall(r'\d+\.?\d*', text)
    operators = re.findall(r'[<>=!]+', text)

    keywords = []
    for pattern in code_patterns + quoted + numbers + operators:
        if len(pattern) >= min_length:
            keywords.append(pattern)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for kw in keywords:
        if kw.lower() not in seen:
            seen.add(kw.lower())
            unique.append(kw)

    return unique[:10]  # Limit to 10 keywords


def extract_keywords_from_critique(critique_path: Path) -> list[str]:
    """Extract keywords from expected_critique.md.

    Args:
        critique_path: Path to expected_critique.md

    Returns:
        List of keywords
    """
    if not critique_path.exists():
        return []

    content = critique_path.read_text()

    # Extract from "Key Points" or "Essential Finding" sections
    keywords = []

    # Look for code blocks
    code_blocks = re.findall(r'```[^`]*```', content, re.DOTALL)
    for block in code_blocks:
        keywords.extend(extract_keywords_from_text(block))

    # Look for backtick-quoted code
    inline_code = re.findall(r'`([^`]+)`', content)
    keywords.extend(inline_code)

    # Look for bullet points with keywords
    bullets = re.findall(r'[-*]\s*(.+)', content)
    for bullet in bullets:
        keywords.extend(extract_keywords_from_text(bullet))

    # Deduplicate
    seen = set()
    unique = []
    for kw in keywords:
        kw_clean = kw.strip()
        if kw_clean and kw_clean.lower() not in seen and len(kw_clean) >= 2:
            seen.add(kw_clean.lower())
            unique.append(kw_clean)

    return unique[:15]


def generate_must_find_entry(meta: dict[str, Any], critique_path: Path) -> dict[str, Any] | None:
    """Generate a must_find entry from meta.json and expected_critique.md.

    Args:
        meta: meta.json content
        critique_path: Path to expected_critique.md

    Returns:
        must_find entry dict or None for FP cases
    """
    # Skip false positive cases
    if not meta.get("expected_detection", True):
        return None

    case_id = meta.get("case_id", "unknown")
    category = meta.get("category", "other")
    severity = meta.get("severity", "major")

    # Map category
    mapped_category = CATEGORY_MAP.get(category, "logic_error")
    if mapped_category is None:
        return None

    # Collect keywords
    keywords = []

    # From bug_anchor (most important)
    bug_anchor = meta.get("bug_anchor", "")
    if bug_anchor:
        keywords.extend(extract_keywords_from_text(bug_anchor))

    # From bug_description
    bug_desc = meta.get("bug_description", "")
    if bug_desc:
        keywords.extend(extract_keywords_from_text(bug_desc))

    # From expected_critique.md
    critique_keywords = extract_keywords_from_critique(critique_path)
    keywords.extend(critique_keywords)

    # Deduplicate keywords
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw.lower() not in seen:
            seen.add(kw.lower())
            unique_keywords.append(kw)

    # Limit keywords
    unique_keywords = unique_keywords[:8]

    # Map severity
    severity_map = {
        "critical": "critical",
        "high": "major",
        "medium": "major",
        "low": "minor",
    }
    mapped_severity = severity_map.get(severity.lower() if severity else "major", "major")

    # Create entry
    entry_id = f"{case_id.lower()}_main"

    return {
        "id": entry_id,
        "category": mapped_category,
        "keywords": unique_keywords,
        "severity_expected": mapped_severity,
        "description": bug_desc or f"Main issue for {case_id}",
        "required": True,
    }


def generate_must_find_with_llm(
    meta: dict[str, Any],
    critique_content: str,
    impl_content: str,
) -> list[dict[str, Any]]:
    """Generate must_find entries using LLM.

    Args:
        meta: meta.json content
        critique_content: Content of expected_critique.md
        impl_content: Content of impl.rb

    Returns:
        List of must_find entries
    """
    try:
        import anthropic
    except ImportError:
        print("Warning: anthropic not installed, falling back to rule-based generation")
        return []

    if not meta.get("expected_detection", True):
        return []

    prompt = f"""Analyze the following bug case and generate structured must_find entries.

## Case Info
- Case ID: {meta.get('case_id')}
- Category: {meta.get('category')}
- Severity: {meta.get('severity')}
- Bug Description: {meta.get('bug_description')}
- Bug Anchor: {meta.get('bug_anchor')}

## Expected Critique (Ground Truth)
{critique_content[:2000]}

## Code Under Review
```ruby
{impl_content[:3000]}
```

## Task
Generate 1-2 must_find entries that capture the essential issues a reviewer should identify.

Each entry should have:
- id: A snake_case identifier (e.g., "discount_inverted", "missing_auth_check")
- category: One of: calculation_error, logic_error, security, performance, data_integrity, race_condition, null_handling, boundary_condition, state_management, authorization, validation, external_api, transaction, concurrency, time_handling, notification
- keywords: 3-6 specific keywords that should appear in a correct review (code snippets, method names, values)
- severity_expected: critical, major, or minor
- description: Brief description of what should be found

## Output Format
Return ONLY valid JSON:
```json
{{
  "must_find": [
    {{
      "id": "example_id",
      "category": "logic_error",
      "keywords": ["keyword1", "keyword2"],
      "severity_expected": "major",
      "description": "Description of the issue"
    }}
  ]
}}
```
"""

    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = message.content[0].text

        # Extract JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(1))
            return parsed.get("must_find", [])

        # Try direct parse
        parsed = json.loads(response_text)
        return parsed.get("must_find", [])

    except Exception as e:
        print(f"  LLM generation failed: {e}")
        return []


def migrate_case(
    case_dir: Path,
    dry_run: bool = True,
    use_llm: bool = False,
) -> bool:
    """Migrate a single case to add must_find.

    Args:
        case_dir: Path to case directory
        dry_run: If True, only print changes without writing
        use_llm: If True, use LLM for better generation

    Returns:
        True if migration was successful
    """
    meta_path = case_dir / "meta.json"
    critique_path = case_dir / "expected_critique.md"
    impl_path = case_dir / "impl.rb"

    if not meta_path.exists():
        print(f"  Skip: meta.json not found")
        return False

    meta = json.loads(meta_path.read_text())
    case_id = meta.get("case_id", "unknown")

    # Skip if must_find already exists
    if "must_find" in meta:
        print(f"  Skip: must_find already exists")
        return True

    # Skip FP cases
    if not meta.get("expected_detection", True):
        print(f"  Skip: False positive case (no must_find needed)")
        return True

    # Generate must_find
    if use_llm and critique_path.exists() and impl_path.exists():
        critique_content = critique_path.read_text()
        impl_content = impl_path.read_text()
        must_find_entries = generate_must_find_with_llm(meta, critique_content, impl_content)

        if not must_find_entries:
            # Fallback to rule-based
            entry = generate_must_find_entry(meta, critique_path)
            must_find_entries = [entry] if entry else []
    else:
        entry = generate_must_find_entry(meta, critique_path)
        must_find_entries = [entry] if entry else []

    if not must_find_entries:
        print(f"  Skip: Could not generate must_find")
        return False

    # Add must_find to meta
    meta["must_find"] = must_find_entries

    if dry_run:
        print(f"  Would add must_find:")
        for entry in must_find_entries:
            print(f"    - {entry['id']}: {entry['category']} ({entry['severity_expected']})")
            print(f"      keywords: {entry['keywords'][:5]}...")
    else:
        # Write updated meta.json
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
        print(f"  Added must_find with {len(must_find_entries)} entries")

    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate meta.json to add must_find field")
    parser.add_argument(
        "--case",
        type=str,
        help="Migrate specific case (e.g., CALC_001)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Migrate all cases",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing",
    )
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Use LLM for better must_find generation",
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Migrate only cases of specific category",
    )

    args = parser.parse_args()

    if not args.case and not args.all:
        parser.print_help()
        print("\nError: Specify --case CASE_ID or --all")
        sys.exit(1)

    # Find case directories
    case_dirs = []
    if args.case:
        for meta_file in CASES_DIR.rglob("meta.json"):
            meta = json.loads(meta_file.read_text())
            if meta.get("case_id") == args.case:
                case_dirs.append(meta_file.parent)
                break
        if not case_dirs:
            print(f"Error: Case not found: {args.case}")
            sys.exit(1)
    else:
        for meta_file in sorted(CASES_DIR.rglob("meta.json")):
            meta = json.loads(meta_file.read_text())
            if args.category and meta.get("category") != args.category:
                continue
            case_dirs.append(meta_file.parent)

    # Summary
    print(f"Found {len(case_dirs)} cases to migrate")
    if args.dry_run:
        print("DRY RUN MODE - No changes will be written\n")
    if args.use_llm:
        print("Using LLM for generation (slower, better quality)\n")

    # Migrate
    success = 0
    failed = 0
    for case_dir in case_dirs:
        meta = json.loads((case_dir / "meta.json").read_text())
        case_id = meta.get("case_id", "unknown")
        print(f"\n[{case_id}] {case_dir.name}")

        if migrate_case(case_dir, dry_run=args.dry_run, use_llm=args.use_llm):
            success += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"Migration complete: {success} succeeded, {failed} failed")
    if args.dry_run:
        print("Run without --dry-run to apply changes")


if __name__ == "__main__":
    main()
