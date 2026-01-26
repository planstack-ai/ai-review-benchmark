#!/usr/bin/env python3
"""Generate case catalog documentation from meta.json files.

This script scans the cases directory and generates a comprehensive
markdown catalog with links to each test case.

Usage:
    python scripts/generate_catalog.py
    python scripts/generate_catalog.py --output docs/case-catalog.md
"""

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


# Category order for each axis
SPEC_ALIGNMENT_CATEGORIES = ["CALC", "STOCK", "STATE", "AUTH", "TIME", "NOTIFY"]
IMPLICIT_KNOWLEDGE_CATEGORIES = ["EXT", "PERF", "DATA", "RAILS", "DJANGO", "LARAVEL"]
FP_CATEGORIES = ["FP"]

# Framework-specific implicit knowledge categories
FRAMEWORK_IMPLICIT_CATEGORIES = {
    "rails": ["EXT", "PERF", "DATA", "RAILS"],
    "laravel": ["EXT", "PERF", "DATA", "LARAVEL"],
    "django": ["DJANGO"],
}

# Framework-specific spec alignment categories
FRAMEWORK_SPEC_CATEGORIES = {
    "rails": SPEC_ALIGNMENT_CATEGORIES,
    "laravel": ["CALC", "STOCK", "STATE", "AUTH", "TIME", "NOTIFY"],
    "django": ["CALC", "AUTH"],
}

# Category display names
CATEGORY_NAMES = {
    "CALC": "Price Calculation",
    "STOCK": "Inventory & Quantity",
    "STATE": "State Transitions",
    "AUTH": "Authorization",
    "TIME": "Time & Duration",
    "NOTIFY": "Notifications",
    "EXT": "External Integration",
    "PERF": "Performance",
    "DATA": "Data Integrity",
    "RAILS": "Rails-Specific",
    "DJANGO": "Django-Specific",
    "LARAVEL": "Laravel-Specific",
    "FP": "False Positive",
}


def load_cases(cases_dir: Path) -> dict[str, list[dict]]:
    """Load all cases from the cases directory.

    Args:
        cases_dir: Path to the cases directory.

    Returns:
        Dictionary mapping framework to list of case metadata.
    """
    cases: dict[str, list[dict]] = defaultdict(list)

    for framework_dir in cases_dir.iterdir():
        if not framework_dir.is_dir():
            continue

        framework = framework_dir.name

        for case_dir in sorted(framework_dir.iterdir()):
            if not case_dir.is_dir():
                continue

            meta_path = case_dir / "meta.json"
            if not meta_path.exists():
                continue

            with open(meta_path) as f:
                meta = json.load(f)
                meta["_path"] = str(case_dir.relative_to(cases_dir.parent))
                cases[framework].append(meta)

    return dict(cases)


def get_category_prefix(case_id: str) -> str:
    """Extract category prefix from case ID.

    Args:
        case_id: Case ID like "CALC_001".

    Returns:
        Category prefix like "CALC".
    """
    return case_id.rsplit("_", 1)[0]


def group_by_axis_and_category(
    cases: list[dict],
) -> dict[str, dict[str, list[dict]]]:
    """Group cases by axis and category.

    Args:
        cases: List of case metadata dictionaries.

    Returns:
        Nested dictionary: axis -> category -> list of cases.
    """
    grouped: dict[str, dict[str, list[dict]]] = {
        "spec_alignment": defaultdict(list),
        "implicit_knowledge": defaultdict(list),
        "false_positive": defaultdict(list),
    }

    for case in cases:
        axis = case.get("axis")
        category = get_category_prefix(case["case_id"])

        if axis == "spec_alignment":
            grouped["spec_alignment"][category].append(case)
        elif axis == "implicit_knowledge":
            grouped["implicit_knowledge"][category].append(case)
        else:
            grouped["false_positive"][category].append(case)

    return grouped


def generate_case_table(cases: list[dict], framework: str) -> str:
    """Generate markdown table for a list of cases.

    Args:
        cases: List of case metadata.
        framework: Framework name for link paths.

    Returns:
        Markdown table string.
    """
    lines = [
        "| Case ID | Severity | Difficulty | Description | Tags | Mode |",
        "|---------|----------|------------|-------------|------|------|",
    ]

    for case in sorted(cases, key=lambda x: x["case_id"]):
        case_id = case["case_id"]
        link = f"[{case_id}](../cases/{framework}/{case_id}/plan.md)"
        severity = case.get("severity") or "-"
        difficulty = case.get("difficulty", "medium")
        description = case.get("bug_description") or case.get("name", "-")
        if len(description) > 50:
            description = description[:47] + "..."
        tags = ", ".join(case.get("tags", [])[:3])
        mode = case.get("evaluation_mode", "severity")

        lines.append(
            f"| {link} | {severity} | {difficulty} | {description} | {tags} | {mode} |"
        )

    return "\n".join(lines)


def generate_summary_table(all_cases: dict[str, list[dict]]) -> str:
    """Generate summary statistics table.

    Args:
        all_cases: Dictionary mapping framework to cases.

    Returns:
        Markdown table string.
    """
    lines = [
        "| Framework | Bug Cases | FP Cases | Total |",
        "|-----------|-----------|----------|-------|",
    ]

    for framework, cases in sorted(all_cases.items()):
        bug_count = sum(1 for c in cases if c.get("expected_detection", True))
        fp_count = sum(1 for c in cases if not c.get("expected_detection", True))
        total = len(cases)
        lines.append(f"| {framework.title()} | {bug_count} | {fp_count} | {total} |")

    # Total row
    all_bugs = sum(
        1 for cases in all_cases.values() for c in cases if c.get("expected_detection", True)
    )
    all_fps = sum(
        1 for cases in all_cases.values() for c in cases if not c.get("expected_detection", True)
    )
    all_total = sum(len(cases) for cases in all_cases.values())
    lines.append(f"| **Total** | **{all_bugs}** | **{all_fps}** | **{all_total}** |")

    return "\n".join(lines)


def generate_index_by_field(
    all_cases: dict[str, list[dict]], field: str, title: str
) -> str:
    """Generate index table grouped by a specific field.

    Args:
        all_cases: Dictionary mapping framework to cases.
        field: Field name to group by.
        title: Section title.

    Returns:
        Markdown section string.
    """
    grouped: dict[str, list[tuple[str, dict]]] = defaultdict(list)

    for framework, cases in all_cases.items():
        for case in cases:
            value = case.get(field)
            if value:
                grouped[value].append((framework, case))

    lines = [f"### {title}", ""]

    for value in sorted(grouped.keys()):
        items = grouped[value]
        case_links = [
            f"[{c['case_id']}](../cases/{fw}/{c['case_id']}/plan.md)"
            for fw, c in sorted(items, key=lambda x: x[1]["case_id"])
        ]
        lines.append(f"**{value}** ({len(items)}): {', '.join(case_links)}")
        lines.append("")

    return "\n".join(lines)


def generate_catalog(cases_dir: Path) -> str:
    """Generate the complete catalog markdown.

    Args:
        cases_dir: Path to the cases directory.

    Returns:
        Complete markdown document string.
    """
    all_cases = load_cases(cases_dir)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sections = [
        "# Test Case Catalog",
        "",
        f"*Generated: {timestamp}*",
        "",
        "This document provides a comprehensive reference for all test cases in the benchmark.",
        "",
        "### Evaluation Mode",
        "",
        "| Mode | Description |",
        "|------|-------------|",
        "| `severity` | Keyword & severity-based automatic evaluation |",
        "| `semantic` | LLM-based semantic evaluation vs `expected_critique.md` |",
        "| `dual` | Explicit + implicit context comparison (for Implicit Knowledge cases) |",
        "",
        "## Summary",
        "",
        generate_summary_table(all_cases),
        "",
        "> Counts are derived from case metadata and updated automatically by `scripts/generate_catalog.py`.",
        "",
    ]

    # Framework sections
    for framework in ["rails", "laravel", "django"]:
        if framework not in all_cases:
            continue

        cases = all_cases[framework]
        grouped = group_by_axis_and_category(cases)

        sections.extend([
            f"## {framework.title()} Cases",
            "",
        ])

        # Spec Alignment
        spec_categories = FRAMEWORK_SPEC_CATEGORIES.get(
            framework, SPEC_ALIGNMENT_CATEGORIES
        )
        spec_cases = grouped["spec_alignment"]
        if any(spec_cases.get(cat) for cat in spec_categories):
            sections.extend([
                "### Spec Alignment",
                "",
                "Cases that test Plan vs Code alignment.",
                "",
            ])

            for category in spec_categories:
                if category in spec_cases and spec_cases[category]:
                    cat_name = CATEGORY_NAMES.get(category, category)
                    count = len(spec_cases[category])
                    sections.extend([
                        f"#### {category} - {cat_name} ({count})",
                        "",
                        generate_case_table(spec_cases[category], framework),
                        "",
                    ])

        # Implicit Knowledge
        impl_categories = FRAMEWORK_IMPLICIT_CATEGORIES.get(
            framework, IMPLICIT_KNOWLEDGE_CATEGORIES
        )
        impl_cases = grouped["implicit_knowledge"]
        if any(impl_cases.get(cat) for cat in impl_categories):
            sections.extend([
                "### Implicit Knowledge",
                "",
                "Cases that test detection of issues not explicitly in Plan.",
                "",
            ])

            for category in impl_categories:
                if category in impl_cases and impl_cases[category]:
                    cat_name = CATEGORY_NAMES.get(category, category)
                    count = len(impl_cases[category])
                    sections.extend([
                        f"#### {category} - {cat_name} ({count})",
                        "",
                        generate_case_table(impl_cases[category], framework),
                        "",
                    ])

        # False Positive
        fp_cases = grouped["false_positive"]
        if fp_cases.get("FP"):
            count = len(fp_cases["FP"])
            sections.extend([
                "### False Positive",
                "",
                "Clean code cases to test for over-detection.",
                "",
                f"#### FP - False Positive ({count})",
                "",
                generate_case_table(fp_cases["FP"], framework),
                "",
            ])

    # Index sections
    sections.extend([
        "## Indexes",
        "",
        generate_index_by_field(all_cases, "severity", "By Severity"),
        generate_index_by_field(all_cases, "difficulty", "By Difficulty"),
        generate_index_by_field(all_cases, "evaluation_mode", "By Evaluation Mode"),
    ])

    return "\n".join(sections)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate case catalog from meta.json files."
    )
    parser.add_argument(
        "--cases-dir",
        type=Path,
        default=Path("cases"),
        help="Path to cases directory (default: cases)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/case-catalog.md"),
        help="Output file path (default: docs/case-catalog.md)",
    )

    args = parser.parse_args()

    # Resolve paths relative to script location
    script_dir = Path(__file__).parent.parent
    cases_dir = script_dir / args.cases_dir
    output_path = script_dir / args.output

    if not cases_dir.exists():
        print(f"Error: Cases directory not found: {cases_dir}")
        return

    catalog = generate_catalog(cases_dir)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(catalog)

    print(f"Generated catalog: {output_path}")

    # Print summary
    all_cases = load_cases(cases_dir)
    total = sum(len(cases) for cases in all_cases.values())
    print(f"Total cases: {total}")
    for framework, cases in sorted(all_cases.items()):
        print(f"  {framework}: {len(cases)}")


if __name__ == "__main__":
    main()
