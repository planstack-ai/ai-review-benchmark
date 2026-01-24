#!/usr/bin/env python3
"""
ベンチマーク実行スクリプト

Usage:
    python scripts/runner.py --model claude-sonnet --cases cases/rails/
    python scripts/runner.py --model deepseek-v3 --cases cases/rails/plan_mismatch/
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Literal

import anthropic
# import openai  # DeepSeek uses OpenAI-compatible API
# import google.generativeai as genai


ModelName = Literal["claude-sonnet", "deepseek-v3", "deepseek-r1", "gemini-pro"]

CASES_DIR = Path(__file__).parent.parent / "cases" / "rails"
RESULTS_DIR = Path(__file__).parent.parent / "results"


REVIEW_PROMPT_TEMPLATE = """あなたはシニアRailsエンジニアです。
以下のコードをレビューしてください。

## 仕様書（Plan）
{plan}

## 既存コードベース情報
{context}

## レビュー対象コード
```ruby
{impl}
```

## 出力形式
以下のJSON形式で回答してください：
```json
{{
  "has_issues": true/false,
  "issues": [
    {{
      "severity": "critical/major/minor",
      "type": "plan_mismatch/logic_bug/security/performance",
      "location": "行番号",
      "description": "問題の説明",
      "suggestion": "修正提案"
    }}
  ],
  "summary": "全体的な所見"
}}
```
"""


def load_case(case_dir: Path) -> dict:
    """ケースファイルを読み込み"""
    return {
        "plan": (case_dir / "plan.md").read_text(),
        "context": (case_dir / "context.md").read_text(),
        "impl": (case_dir / "impl.rb").read_text(),
        "meta": json.loads((case_dir / "meta.json").read_text()),
    }


def build_prompt(case: dict) -> str:
    """レビュープロンプトを構築"""
    return REVIEW_PROMPT_TEMPLATE.format(
        plan=case["plan"],
        context=case["context"],
        impl=case["impl"],
    )


def call_claude_sonnet(prompt: str) -> dict:
    """Claude Sonnet APIを呼び出し"""
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    # TODO: JSON抽出
    return {"raw_response": message.content[0].text}


def call_deepseek_v3(prompt: str) -> dict:
    """DeepSeek V3 APIを呼び出し"""
    # TODO: 実装
    return {"raw_response": ""}


def call_deepseek_r1(prompt: str) -> dict:
    """DeepSeek R1 APIを呼び出し"""
    # TODO: 実装
    return {"raw_response": ""}


def call_gemini_pro(prompt: str) -> dict:
    """Gemini Pro APIを呼び出し"""
    # TODO: 実装
    return {"raw_response": ""}


def run_review(model: ModelName, case: dict) -> dict:
    """モデルでレビューを実行"""
    prompt = build_prompt(case)

    if model == "claude-sonnet":
        return call_claude_sonnet(prompt)
    elif model == "deepseek-v3":
        return call_deepseek_v3(prompt)
    elif model == "deepseek-r1":
        return call_deepseek_r1(prompt)
    elif model == "gemini-pro":
        return call_gemini_pro(prompt)
    else:
        raise ValueError(f"Unknown model: {model}")


def discover_cases(cases_path: Path) -> list[Path]:
    """ケースディレクトリを探索"""
    case_dirs = []
    for meta_file in cases_path.rglob("meta.json"):
        case_dirs.append(meta_file.parent)
    return sorted(case_dirs)


def main() -> None:
    parser = argparse.ArgumentParser(description="ベンチマーク実行")
    parser.add_argument(
        "--model",
        choices=["claude-sonnet", "deepseek-v3", "deepseek-r1", "gemini-pro"],
        required=True,
        help="使用するモデル",
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=CASES_DIR,
        help="ケースディレクトリのパス",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="結果出力ディレクトリ（デフォルト: results/{timestamp}_run/）",
    )

    args = parser.parse_args()

    # 出力ディレクトリ設定
    if args.output_dir:
        output_dir = args.output_dir
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = RESULTS_DIR / f"{timestamp}_run"
    output_dir.mkdir(parents=True, exist_ok=True)

    # ケース探索
    case_dirs = discover_cases(args.cases)
    print(f"Found {len(case_dirs)} cases")

    # 実行
    results = []
    for case_dir in case_dirs:
        print(f"Running: {case_dir.name}")
        case = load_case(case_dir)
        result = run_review(args.model, case)
        result["case_id"] = case["meta"]["case_id"]
        result["category"] = case["meta"]["category"]
        results.append(result)

    # 結果保存
    output_file = output_dir / f"{args.model}.json"
    output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
