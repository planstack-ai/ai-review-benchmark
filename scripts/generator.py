#!/usr/bin/env python3
"""
テストケース生成スクリプト

Usage:
    python scripts/generator.py --category plan_mismatch --count 20
    python scripts/generator.py --all
"""

import argparse
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Literal


Category = Literal["plan_mismatch", "logic_bug", "false_positive"]

CASES_DIR = Path(__file__).parent.parent / "cases" / "rails"


@dataclass
class TestCase:
    case_id: str
    category: Category
    difficulty: Literal["easy", "medium", "hard"]
    expected_detection: bool
    bug_description: str
    bug_location: str
    correct_implementation: str
    tags: list[str]
    notes: str


def generate_plan_mismatch_cases(count: int) -> list[TestCase]:
    """Plan不整合ケースを生成"""
    # TODO: 実装
    cases = []
    return cases


def generate_logic_bug_cases(count: int) -> list[TestCase]:
    """論理バグケースを生成"""
    # TODO: 実装
    cases = []
    return cases


def generate_false_positive_cases(count: int) -> list[TestCase]:
    """False Positiveケースを生成"""
    # TODO: 実装
    cases = []
    return cases


def write_case_files(case: TestCase, case_dir: Path) -> None:
    """ケースファイルを出力"""
    case_dir.mkdir(parents=True, exist_ok=True)

    # plan.md
    (case_dir / "plan.md").write_text("# TODO: 仕様書\n")

    # context.md
    (case_dir / "context.md").write_text("# TODO: コンテキスト情報\n")

    # impl.rb
    (case_dir / "impl.rb").write_text("# TODO: 実装コード\n")

    # meta.json
    meta = {
        "case_id": case.case_id,
        "category": case.category,
        "difficulty": case.difficulty,
        "expected_detection": case.expected_detection,
        "bug_description": case.bug_description,
        "bug_location": case.bug_location,
        "correct_implementation": case.correct_implementation,
        "tags": case.tags,
        "notes": case.notes,
    }
    (case_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="テストケース生成")
    parser.add_argument(
        "--category",
        choices=["plan_mismatch", "logic_bug", "false_positive"],
        help="生成するカテゴリ",
    )
    parser.add_argument("--count", type=int, default=20, help="生成するケース数")
    parser.add_argument("--all", action="store_true", help="全カテゴリを生成")

    args = parser.parse_args()

    if args.all:
        categories = ["plan_mismatch", "logic_bug", "false_positive"]
    elif args.category:
        categories = [args.category]
    else:
        parser.print_help()
        return

    for category in categories:
        print(f"Generating {category} cases...")
        if category == "plan_mismatch":
            cases = generate_plan_mismatch_cases(args.count)
        elif category == "logic_bug":
            cases = generate_logic_bug_cases(args.count)
        else:
            cases = generate_false_positive_cases(args.count)

        for case in cases:
            case_dir = CASES_DIR / category / case.case_id
            write_case_files(case, case_dir)
            print(f"  Created: {case_dir}")

    print("Done!")


if __name__ == "__main__":
    main()
