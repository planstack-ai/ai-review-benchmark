#!/usr/bin/env python3
"""
ベンチマーク実行スクリプト

Usage:
    python scripts/runner.py --model claude-sonnet --cases cases/rails/
    python scripts/runner.py --model deepseek-v3 --cases cases/rails/plan_mismatch/
    python scripts/runner.py --model all --cases cases/rails/
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(Path(__file__).parent.parent / ".env")

import anthropic
import google.generativeai as genai
import openai

ModelName = Literal["claude-opus", "claude-sonnet", "claude-haiku", "gpt-4o", "gpt-5", "deepseek-v3", "deepseek-r1", "gemini-pro", "gemini-3-pro", "gemini-3-flash"]
ALL_MODELS: list[ModelName] = ["claude-opus", "claude-sonnet", "claude-haiku", "gpt-4o", "gpt-5", "deepseek-v3", "deepseek-r1", "gemini-pro", "gemini-3-pro", "gemini-3-flash"]

RunMode = Literal["explicit", "implicit", "dual"]
FrameworkName = Literal["rails", "django"]

RESULTS_DIR = Path(__file__).parent.parent / "results"

# Framework configuration
FRAMEWORK_CONFIG = {
    "rails": {
        "impl_ext": ".rb",
        "language": "Ruby",
        "code_block": "ruby",
    },
    "django": {
        "impl_ext": ".py",
        "language": "Python",
        "code_block": "python",
    },
}


def get_cases_dir(framework: str) -> Path:
    """Get the cases directory for a framework."""
    return Path(__file__).parent.parent / "cases" / framework


# Default for backward compatibility
CASES_DIR = get_cases_dir("rails")

# モデル設定
MODEL_CONFIG = {
    "claude-opus": {
        "model_id": "claude-opus-4-5-20251101",
        "input_cost_per_1m": 5.00,
        "output_cost_per_1m": 25.00,
    },
    "claude-sonnet": {
        "model_id": "claude-sonnet-4-20250514",
        "input_cost_per_1m": 3.00,
        "output_cost_per_1m": 15.00,
    },
    "claude-haiku": {
        "model_id": "claude-haiku-4-5-20251001",
        "input_cost_per_1m": 1.00,
        "output_cost_per_1m": 5.00,
    },
    "gpt-4o": {
        "model_id": "gpt-4o",
        "input_cost_per_1m": 2.50,
        "output_cost_per_1m": 10.00,
    },
    "gpt-5": {
        "model_id": "gpt-5",
        "input_cost_per_1m": 1.25,
        "output_cost_per_1m": 10.00,
    },
    "deepseek-v3": {
        "model_id": "deepseek-chat",
        "base_url": "https://api.deepseek.com",
        "input_cost_per_1m": 0.14,
        "output_cost_per_1m": 0.28,
    },
    "deepseek-r1": {
        "model_id": "deepseek-reasoner",
        "base_url": "https://api.deepseek.com",
        "input_cost_per_1m": 0.55,
        "output_cost_per_1m": 2.19,
    },
    "gemini-pro": {
        "model_id": "gemini-2.5-pro",
        "input_cost_per_1m": 1.25,
        "output_cost_per_1m": 5.00,
    },
    "gemini-3-pro": {
        "model_id": "gemini-3-pro-preview",
        "input_cost_per_1m": 1.25,
        "output_cost_per_1m": 10.00,
    },
    "gemini-3-flash": {
        "model_id": "gemini-3-flash-preview",
        "input_cost_per_1m": 0.10,
        "output_cost_per_1m": 0.40,
    },
}

# Rails review prompt templates
REVIEW_PROMPT_RAILS_TEMPLATE = """あなたはシニアRailsエンジニアです。
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
以下のJSON形式で回答してください。JSON以外の文章は含めないでください：
```json
{{
  "has_issues": true/false,
  "issues": [
    {{
      "severity": "critical/major/minor",
      "type": "plan_mismatch/logic_bug/security/performance",
      "location": "行番号または該当箇所",
      "description": "問題の説明",
      "suggestion": "修正提案"
    }}
  ],
  "summary": "全体的な所見"
}}
```

問題がない場合は has_issues を false にし、issues を空配列にしてください。
"""

# Django review prompt templates
REVIEW_PROMPT_DJANGO_TEMPLATE = """You are a Senior Django Developer.
Review the following Python code against the specification.

## Specification (Plan)
{plan}

## Existing Codebase Context
{context}

## Code Under Review
```python
{impl}
```

## Output Format
Respond with ONLY the following JSON format (no other text):
```json
{{
  "has_issues": true/false,
  "issues": [
    {{
      "severity": "critical/major/minor",
      "type": "plan_mismatch/logic_bug/security/performance",
      "location": "line number or code location",
      "description": "description of the issue",
      "suggestion": "suggested fix"
    }}
  ],
  "summary": "overall findings"
}}
```

If there are no issues, set has_issues to false and issues to an empty array.
"""

# Backward compatibility alias
REVIEW_PROMPT_TEMPLATE = REVIEW_PROMPT_RAILS_TEMPLATE

REVIEW_PROMPT_DIFF_RAILS_TEMPLATE = """あなたはシニアRailsエンジニアです。
以下のPull Requestをレビューしてください。

## 仕様書（Plan）
{plan}

## 既存コードベース情報
{context}

## PR差分
```diff
{diff}
```

## 出力形式
以下のJSON形式で回答してください。JSON以外の文章は含めないでください：
```json
{{
  "has_issues": true/false,
  "issues": [
    {{
      "severity": "critical/major/minor",
      "type": "plan_mismatch/logic_bug/security/performance",
      "location": "ファイル名:行番号または該当箇所",
      "description": "問題の説明",
      "suggestion": "修正提案"
    }}
  ],
  "summary": "全体的な所見"
}}
```

問題がない場合は has_issues を false にし、issues を空配列にしてください。
"""

REVIEW_PROMPT_DIFF_DJANGO_TEMPLATE = """You are a Senior Django Developer.
Review the following Pull Request against the specification.

## Specification (Plan)
{plan}

## Existing Codebase Context
{context}

## PR Diff
```diff
{diff}
```

## Output Format
Respond with ONLY the following JSON format (no other text):
```json
{{
  "has_issues": true/false,
  "issues": [
    {{
      "severity": "critical/major/minor",
      "type": "plan_mismatch/logic_bug/security/performance",
      "location": "filename:line number or code location",
      "description": "description of the issue",
      "suggestion": "suggested fix"
    }}
  ],
  "summary": "overall findings"
}}
```

If there are no issues, set has_issues to false and issues to an empty array.
"""

# Backward compatibility alias
REVIEW_PROMPT_DIFF_TEMPLATE = REVIEW_PROMPT_DIFF_RAILS_TEMPLATE


def load_case(case_dir: Path, mode: RunMode = "explicit", framework: str = "rails") -> dict[str, Any]:
    """ケースファイルを読み込み

    Args:
        case_dir: ケースディレクトリのパス
        mode: 実行モード
            - "explicit": context.md（ガイドライン含む）を使用
            - "implicit": context_base.md（ガイドラインなし）を使用
            - "dual": 呼び出し元で両方実行
        framework: フレームワーク（rails または django）

    Returns:
        ケースデータの辞書
    """
    meta = json.loads((case_dir / "meta.json").read_text())

    # モードに応じたcontextファイルを選択
    context_file = case_dir / "context.md"  # デフォルト

    if mode == "implicit":
        # implicit モードでは context_base.md を使用（なければ context.md にフォールバック）
        context_base_file = case_dir / "context_base.md"
        if context_base_file.exists():
            context_file = context_base_file

    # Determine implementation file based on framework
    framework_cfg = FRAMEWORK_CONFIG.get(framework, FRAMEWORK_CONFIG["rails"])
    impl_ext = framework_cfg["impl_ext"]
    impl_file = case_dir / f"impl{impl_ext}"

    # Fallback: try both extensions if primary doesn't exist
    if not impl_file.exists():
        alt_ext = ".py" if impl_ext == ".rb" else ".rb"
        alt_impl_file = case_dir / f"impl{alt_ext}"
        if alt_impl_file.exists():
            impl_file = alt_impl_file

    case_data = {
        "plan": (case_dir / "plan.md").read_text(),
        "context": context_file.read_text(),
        "impl": impl_file.read_text(),
        "meta": meta,
        "context_mode": mode,
        "context_file": context_file.name,
        "framework": framework,
    }

    # オプション: diff があれば読み込み
    diff_file = case_dir / "pr.diff"
    if diff_file.exists():
        case_data["diff"] = diff_file.read_text()

    # オプション: rubric があれば読み込み
    rubric_file = case_dir / "rubric.json"
    if rubric_file.exists():
        case_data["rubric"] = json.loads(rubric_file.read_text())

    return case_data


def build_prompt(case: dict[str, Any]) -> str:
    """レビュープロンプトを構築"""
    framework = case.get("framework", "rails")

    # Select template based on framework
    if framework == "django":
        impl_template = REVIEW_PROMPT_DJANGO_TEMPLATE
        diff_template = REVIEW_PROMPT_DIFF_DJANGO_TEMPLATE
    else:
        impl_template = REVIEW_PROMPT_RAILS_TEMPLATE
        diff_template = REVIEW_PROMPT_DIFF_RAILS_TEMPLATE

    # diff があれば diff 用テンプレートを使用
    if "diff" in case:
        return diff_template.format(
            plan=case["plan"],
            context=case["context"],
            diff=case["diff"],
        )

    # なければ従来通り impl を使用
    return impl_template.format(
        plan=case["plan"],
        context=case["context"],
        impl=case["impl"],
    )


def extract_json(text: str) -> dict[str, Any] | None:
    """レスポンスからJSONを抽出"""
    # ```json ... ``` ブロックを探す
    json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # ``` ... ``` ブロックを探す
    code_match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if code_match:
        try:
            return json.loads(code_match.group(1))
        except json.JSONDecodeError:
            pass

    # 直接JSONとしてパース
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # { から } までを抽出
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def call_claude(prompt: str, model_name: Literal["claude-opus", "claude-sonnet", "claude-haiku"]) -> dict[str, Any]:
    """Claude APIを呼び出し"""
    client = anthropic.Anthropic()
    config = MODEL_CONFIG[model_name]

    start_time = time.time()
    message = client.messages.create(
        model=config["model_id"],
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed_time = time.time() - start_time

    raw_response = message.content[0].text
    parsed = extract_json(raw_response)

    return {
        "raw_response": raw_response,
        "parsed_response": parsed,
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
        "elapsed_time": elapsed_time,
        "cost": (
            message.usage.input_tokens * config["input_cost_per_1m"] / 1_000_000
            + message.usage.output_tokens * config["output_cost_per_1m"] / 1_000_000
        ),
    }


def call_openai(prompt: str, model_name: Literal["gpt-4o", "gpt-5"]) -> dict[str, Any]:
    """OpenAI APIを呼び出し"""
    config = MODEL_CONFIG[model_name]

    client = openai.OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    start_time = time.time()
    response = client.chat.completions.create(
        model=config["model_id"],
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed_time = time.time() - start_time

    raw_response = response.choices[0].message.content or ""
    parsed = extract_json(raw_response)

    input_tokens = response.usage.prompt_tokens if response.usage else 0
    output_tokens = response.usage.completion_tokens if response.usage else 0

    return {
        "raw_response": raw_response,
        "parsed_response": parsed,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "elapsed_time": elapsed_time,
        "cost": (
            input_tokens * config["input_cost_per_1m"] / 1_000_000
            + output_tokens * config["output_cost_per_1m"] / 1_000_000
        ),
    }


def call_deepseek(prompt: str, model_name: Literal["deepseek-v3", "deepseek-r1"]) -> dict[str, Any]:
    """DeepSeek APIを呼び出し（OpenAI互換）"""
    config = MODEL_CONFIG[model_name]

    client = openai.OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url=config["base_url"],
    )

    start_time = time.time()
    response = client.chat.completions.create(
        model=config["model_id"],
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed_time = time.time() - start_time

    raw_response = response.choices[0].message.content or ""
    parsed = extract_json(raw_response)

    input_tokens = response.usage.prompt_tokens if response.usage else 0
    output_tokens = response.usage.completion_tokens if response.usage else 0

    return {
        "raw_response": raw_response,
        "parsed_response": parsed,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "elapsed_time": elapsed_time,
        "cost": (
            input_tokens * config["input_cost_per_1m"] / 1_000_000
            + output_tokens * config["output_cost_per_1m"] / 1_000_000
        ),
    }


def call_deepseek_v3(prompt: str) -> dict[str, Any]:
    """DeepSeek V3 APIを呼び出し"""
    return call_deepseek(prompt, "deepseek-v3")


def call_deepseek_r1(prompt: str) -> dict[str, Any]:
    """DeepSeek R1 APIを呼び出し"""
    return call_deepseek(prompt, "deepseek-r1")


def call_gemini(prompt: str, model_name: str = "gemini-pro") -> dict[str, Any]:
    """Gemini APIを呼び出し"""
    config = MODEL_CONFIG[model_name]

    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(config["model_id"])

    start_time = time.time()
    response = model.generate_content(prompt)
    elapsed_time = time.time() - start_time

    raw_response = response.text
    parsed = extract_json(raw_response)

    # Gemini のトークン数取得
    input_tokens = response.usage_metadata.prompt_token_count if response.usage_metadata else 0
    output_tokens = response.usage_metadata.candidates_token_count if response.usage_metadata else 0

    return {
        "raw_response": raw_response,
        "parsed_response": parsed,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "elapsed_time": elapsed_time,
        "cost": (
            input_tokens * config["input_cost_per_1m"] / 1_000_000
            + output_tokens * config["output_cost_per_1m"] / 1_000_000
        ),
    }


def run_review(model: ModelName, case: dict[str, Any]) -> dict[str, Any]:
    """モデルでレビューを実行"""
    prompt = build_prompt(case)

    if model in ("claude-opus", "claude-sonnet", "claude-haiku"):
        return call_claude(prompt, model)
    elif model in ("gpt-4o", "gpt-5"):
        return call_openai(prompt, model)
    elif model == "deepseek-v3":
        return call_deepseek_v3(prompt)
    elif model == "deepseek-r1":
        return call_deepseek_r1(prompt)
    elif model in ("gemini-pro", "gemini-3-pro", "gemini-3-flash"):
        return call_gemini(prompt, model)
    else:
        raise ValueError(f"Unknown model: {model}")


def discover_cases(cases_path: Path) -> list[Path]:
    """ケースディレクトリを探索"""
    case_dirs = []
    for meta_file in cases_path.rglob("meta.json"):
        case_dirs.append(meta_file.parent)
    return sorted(case_dirs)


def run_single_case(
    model: ModelName,
    case_dir: Path,
    mode: RunMode,
    verbose: bool = False,
    framework: str = "rails",
) -> dict[str, Any]:
    """単一ケースを実行

    Args:
        model: モデル名
        case_dir: ケースディレクトリ
        mode: 実行モード（explicit/implicit）
        verbose: 詳細出力
        framework: フレームワーク（rails または django）

    Returns:
        実行結果の辞書
    """
    case = load_case(case_dir, mode=mode, framework=framework)
    result = run_review(model, case)

    result["case_id"] = case["meta"]["case_id"]
    result["category"] = case["meta"]["category"]
    result["expected_detection"] = case["meta"]["expected_detection"]
    result["difficulty"] = case["meta"]["difficulty"]
    result["success"] = True
    result["has_diff"] = "diff" in case
    result["has_rubric"] = "rubric" in case
    result["evaluation_mode"] = case["meta"].get("evaluation_mode", "severity")
    result["context_mode"] = mode
    result["context_file"] = case.get("context_file", "context.md")

    return result


def run_benchmark(
    model: ModelName,
    case_dirs: list[Path],
    output_dir: Path,
    mode: RunMode = "explicit",
    verbose: bool = False,
    framework: str = "rails",
) -> dict[str, Any]:
    """単一モデルでベンチマークを実行

    Args:
        model: モデル名
        case_dirs: ケースディレクトリのリスト
        output_dir: 結果出力ディレクトリ
        mode: 実行モード
            - "explicit": ガイドライン有りでレビュー
            - "implicit": ガイドライン無しでレビュー
            - "dual": 両方実行して比較用データを生成
        verbose: 詳細出力
        framework: フレームワーク（rails または django）
    """
    results = []
    total_cost = 0.0
    total_time = 0.0
    errors = []

    mode_suffix = f" [{mode}]" if mode != "explicit" else ""
    print(f"\n{'='*60}")
    print(f"Running: {model}{mode_suffix}")
    print(f"{'='*60}")

    # dual モードでは実行回数が2倍
    modes_to_run: list[RunMode] = ["explicit", "implicit"] if mode == "dual" else [mode]

    for i, case_dir in enumerate(case_dirs, 1):
        case_id = case_dir.name
        category = case_dir.parent.name
        meta = json.loads((case_dir / "meta.json").read_text())

        # dual モード対応ケースかチェック
        is_dual_capable = meta.get("evaluation_mode") == "dual"

        for run_mode in modes_to_run:
            # dual モードでも、dual 非対応ケースは explicit のみ実行
            if mode == "dual" and run_mode == "implicit" and not is_dual_capable:
                continue

            mode_label = f" ({run_mode})" if mode == "dual" else ""
            print(f"[{i:3d}/{len(case_dirs)}] {category}/{case_id}{mode_label}", end=" ... ", flush=True)

            try:
                result = run_single_case(model, case_dir, run_mode, verbose, framework)

                total_cost += result.get("cost", 0)
                total_time += result.get("elapsed_time", 0)

                print(f"OK ({result.get('elapsed_time', 0):.1f}s, ${result.get('cost', 0):.4f})")

                if verbose and result.get("parsed_response"):
                    parsed = result["parsed_response"]
                    if parsed.get("has_issues"):
                        print(f"       Issues found: {len(parsed.get('issues', []))}")

            except Exception as e:
                result = {
                    "case_id": case_dir.name,
                    "category": category,
                    "context_mode": run_mode,
                    "success": False,
                    "error": str(e),
                }
                errors.append(f"{category}/{case_id} ({run_mode}): {e}")
                print(f"ERROR: {e}")

            results.append(result)

    # 結果保存
    # dual モードの場合はファイル名にモードを含めない（結果にcontext_modeが含まれる）
    output_file = output_dir / f"{model}.json"
    output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))

    # サマリー
    actual_runs = len(results)
    summary = {
        "model": model,
        "mode": mode,
        "total_cases": len(case_dirs),
        "total_runs": actual_runs,
        "successful": len([r for r in results if r.get("success")]),
        "failed": len([r for r in results if not r.get("success")]),
        "total_cost": total_cost,
        "total_time": total_time,
        "avg_time_per_run": total_time / actual_runs if actual_runs else 0,
        "errors": errors,
    }

    if mode == "dual":
        explicit_results = [r for r in results if r.get("context_mode") == "explicit"]
        implicit_results = [r for r in results if r.get("context_mode") == "implicit"]
        summary["explicit_runs"] = len(explicit_results)
        summary["implicit_runs"] = len(implicit_results)

    print(f"\n{model} Summary:")
    print(f"  Runs: {summary['successful']}/{summary['total_runs']} successful")
    if mode == "dual":
        print(f"  (explicit: {summary.get('explicit_runs', 0)}, implicit: {summary.get('implicit_runs', 0)})")
    print(f"  Total cost: ${summary['total_cost']:.4f}")
    print(f"  Total time: {summary['total_time']:.1f}s")
    print(f"  Avg time/run: {summary['avg_time_per_run']:.1f}s")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="AIコードレビューベンチマーク実行")
    parser.add_argument(
        "--model",
        choices=["claude-opus", "claude-sonnet", "claude-haiku", "gpt-4o", "gpt-5", "deepseek-v3", "deepseek-r1", "gemini-pro", "gemini-3-pro", "gemini-3-flash", "all"],
        required=True,
        help="使用するモデル（'all'で全モデル実行）",
    )
    parser.add_argument(
        "--mode",
        choices=["explicit", "implicit", "dual"],
        default="explicit",
        help="実行モード: explicit（ガイドライン有り）, implicit（ガイドライン無し）, dual（両方）",
    )
    parser.add_argument(
        "--framework",
        choices=["rails", "django"],
        default="rails",
        help="Target framework (default: rails)",
    )
    parser.add_argument(
        "--cases",
        type=Path,
        help="ケースディレクトリのパス（デフォルト: cases/{framework}）",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="結果出力ディレクトリ（デフォルト: results/{timestamp}_run/）",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="詳細出力",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="API呼び出しをせずにケース一覧のみ表示",
    )

    args = parser.parse_args()

    # Determine cases directory
    if args.cases:
        cases_dir = args.cases
    else:
        cases_dir = get_cases_dir(args.framework)

    # 出力ディレクトリ設定
    if args.output_dir:
        output_dir = args.output_dir
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = RESULTS_DIR / f"{timestamp}_run"

    # ケース探索
    if not cases_dir.exists():
        print(f"Error: Cases directory not found: {cases_dir}", file=sys.stderr)
        sys.exit(1)

    case_dirs = discover_cases(cases_dir)
    print(f"Found {len(case_dirs)} cases in {cases_dir} (framework: {args.framework})")

    if args.dry_run:
        print("\nCases to run:")
        for case_dir in case_dirs:
            print(f"  - {case_dir.parent.name}/{case_dir.name}")
        print(f"\nTotal: {len(case_dirs)} cases")
        return

    # 出力ディレクトリ作成
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # モデル選択
    if args.model == "all":
        models = ALL_MODELS
    else:
        models = [args.model]

    # 実行
    all_summaries = []
    for model in models:
        summary = run_benchmark(model, case_dirs, output_dir, mode=args.mode, verbose=args.verbose, framework=args.framework)
        all_summaries.append(summary)

    # 全体サマリー保存
    summary_file = output_dir / "summary.json"
    summary_data = {
        "timestamp": datetime.now().isoformat(),
        "framework": args.framework,
        "mode": args.mode,
        "total_cases": len(case_dirs),
        "models": all_summaries,
    }
    summary_file.write_text(json.dumps(summary_data, indent=2, ensure_ascii=False))

    print(f"\n{'='*60}")
    print("Benchmark completed!")
    print(f"Results saved to: {output_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
