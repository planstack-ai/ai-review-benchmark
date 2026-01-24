#!/usr/bin/env python3
"""Update meta.json files to conform to benchmark spec v3."""

import json
import re
from pathlib import Path

# Severity mapping based on tags
SEVERITY_RULES = {
    # Critical: Security vulnerabilities, major financial impact
    "critical": [
        "sql_injection", "xss", "security", "session_fixation",
        "mass_assignment", "timing_attack", "race_condition",
        "calculation", "discount", "tax", "currency"
    ],
    # High: Data integrity, functional bugs
    "high": [
        "transaction", "validation", "scope", "query",
        "authorization", "authentication", "redirect"
    ],
    # Medium: Logic errors, moderate impact
    "medium": [
        "loop", "boundary", "off_by_one", "nil", "null",
        "string", "comparison", "operator", "pagination",
        "timezone", "enum", "callback", "format"
    ],
    # Low: Minor issues, optimizations
    "low": [
        "performance", "n_plus_one", "optimization"
    ]
}


def determine_severity(tags: list[str], bug_description: str) -> str:
    """Determine severity based on tags and description."""
    tags_lower = [t.lower() for t in tags]
    desc_lower = bug_description.lower() if bug_description else ""

    for severity, keywords in SEVERITY_RULES.items():
        for keyword in keywords:
            if keyword in tags_lower or keyword in desc_lower:
                return severity

    return "medium"  # Default


def extract_bug_anchor(impl_path: Path, bug_location: str | None) -> str | None:
    """Extract bug anchor code from impl.rb."""
    if not impl_path.exists() or not bug_location:
        return None

    # Parse line number from bug_location (e.g., "impl.rb:16")
    match = re.search(r":(\d+)", bug_location)
    if not match:
        return None

    line_num = int(match.group(1))

    try:
        lines = impl_path.read_text().splitlines()

        # Search for BUG marker in nearby lines (up to 5 lines after)
        for offset in range(6):
            idx = line_num - 1 + offset
            if 0 <= idx < len(lines):
                line = lines[idx]
                if "BUG" in line or "bug" in line.lower():
                    # Found a line with BUG marker - extract the code part
                    code_part = line.split("#")[0].strip()
                    if code_part and not code_part.startswith(("def ", "class ", "end", "private", "protected")):
                        return code_part

        # If no BUG marker found, look for actual code (not method definitions)
        for offset in range(6):
            idx = line_num - 1 + offset
            if 0 <= idx < len(lines):
                line = lines[idx].strip()
                # Skip empty lines, comments, and structural elements
                if not line or line.startswith("#"):
                    continue
                if line.startswith(("def ", "class ", "module ", "end", "private", "protected", "public")):
                    continue

                # Remove trailing comments
                code_part = line.split("#")[0].strip()
                if code_part:
                    return code_part

        # Fallback: use the exact line
        if 0 < line_num <= len(lines):
            line = lines[line_num - 1].strip()
            if "#" in line:
                line = line.split("#")[0].strip()
            return line if line else None

    except Exception:
        pass

    return None


def extract_name(case_dir: Path) -> str:
    """Extract pattern name from directory name."""
    # e.g., "01_discount_rate" -> "discount_rate"
    dir_name = case_dir.name
    match = re.match(r"\d+_(.+)", dir_name)
    return match.group(1) if match else dir_name


def determine_axis(category: str) -> str | None:
    """Determine axis based on category."""
    if category == "plan_mismatch":
        return "spec_alignment"
    elif category == "logic_bug":
        return "implicit_knowledge"
    elif category == "false_positive":
        return None
    return None


def update_meta_json(meta_path: Path) -> dict:
    """Update a single meta.json file."""
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    case_dir = meta_path.parent
    impl_path = case_dir / "impl.rb"
    category = meta.get("category", "")

    # Add missing fields
    updates = {}

    # axis
    if "axis" not in meta:
        axis = determine_axis(category)
        if axis:
            updates["axis"] = axis

    # name
    if "name" not in meta:
        updates["name"] = extract_name(case_dir)

    # severity
    if "severity" not in meta:
        if meta.get("expected_detection", False):
            tags = meta.get("tags", [])
            bug_desc = meta.get("bug_description", "")
            updates["severity"] = determine_severity(tags, bug_desc)
        else:
            updates["severity"] = None

    # bug_anchor - always recalculate for better accuracy
    if meta.get("expected_detection", False):
        bug_location = meta.get("bug_location")
        anchor = extract_bug_anchor(impl_path, bug_location)
        if anchor and anchor != meta.get("bug_anchor"):
            updates["bug_anchor"] = anchor
        elif not anchor and "bug_anchor" not in meta:
            updates["bug_anchor"] = None

    if updates:
        meta.update(updates)

        # Reorder keys for consistency
        key_order = [
            "case_id", "category", "axis", "name", "difficulty",
            "expected_detection", "bug_description", "bug_location",
            "bug_anchor", "correct_implementation", "severity", "tags", "notes"
        ]
        ordered_meta = {}
        for key in key_order:
            if key in meta:
                ordered_meta[key] = meta[key]
        # Add any remaining keys
        for key in meta:
            if key not in ordered_meta:
                ordered_meta[key] = meta[key]

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(ordered_meta, f, ensure_ascii=False, indent=2)
            f.write("\n")

        return updates

    return {}


def main():
    """Main function to update all meta.json files."""
    cases_dir = Path(__file__).parent.parent / "cases" / "rails"
    meta_files = list(cases_dir.glob("**/meta.json"))

    print(f"Found {len(meta_files)} meta.json files")
    print("-" * 60)

    updated_count = 0
    for meta_path in sorted(meta_files):
        relative_path = meta_path.relative_to(cases_dir)
        updates = update_meta_json(meta_path)

        if updates:
            updated_count += 1
            print(f"Updated: {relative_path}")
            for key, value in updates.items():
                print(f"  + {key}: {value}")

    print("-" * 60)
    print(f"Updated {updated_count}/{len(meta_files)} files")


if __name__ == "__main__":
    main()
