#!/usr/bin/env python3
"""
採点スクリプト（LLM-as-a-Judge）

Usage:
    python scripts/evaluator.py --run-dir results/20250124_run/
    python scripts/evaluator.py --run-dir results/20250124_run/ --skip-judge  # Judgeなしで集計のみ
"""

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

import anthropic


CASES_DIR = Path(__file__).parent.parent / "cases" / "rails"

# Judge モデル設定
JUDGE_MODEL = "claude-sonnet-4-20250514"
JUDGE_INPUT_COST_PER_1M = 3.00
JUDGE_OUTPUT_COST_PER_1M = 15.00


JUDGE_PROMPT_TEMPLATE = """あなたはコードレビューの品質を評価する審査員です。
AIレビュアーの出力を評価し、正解と比較してください。

## ケース情報
- カテゴリ: {category}
- 期待される検知: {expected_detection}
- バグの説明: {bug_description}
- バグの場所: {bug_location}

## AIレビュアーの出力
```json
{review_result}
```

## 評価タスク

1. **検知判定**: AIがバグを正しく検知できたか判定してください
   - バグありケース（expected_detection=true）: 該当バグを指摘していれば detected=true
   - バグなしケース（expected_detection=false）: 問題なしと判定していれば detected=true（正しく見逃した）

2. **精度評価**: 指摘内容の正確性を0-100で評価
   - 100: 完璧に正しい指摘
   - 70-99: 本質的に正しいが細部に差異
   - 40-69: 部分的に正しい
   - 0-39: 的外れまたは誤り

3. **ノイズカウント**: 正解に無関係な誤った指摘の数

以下のJSON形式で回答してください。JSON以外は含めないでください：
```json
{{
  "detected": true/false,
  "accuracy": 0-100,
  "noise_count": 0,
  "correct_location": true/false,
  "reasoning": "評価理由（日本語で簡潔に）"
}}
```
"""


@dataclass
class EvaluationResult:
    """単一ケースの評価結果"""
    case_id: str
    category: str
    difficulty: str
    model: str
    expected_detection: bool
    detected: bool
    accuracy: int
    noise_count: int
    correct_location: bool
    reasoning: str
    review_has_issues: bool | None  # AIの判定結果
    review_issue_count: int  # AIが指摘した問題数


@dataclass
class ModelMetrics:
    """モデル全体の評価指標"""
    model: str
    total_cases: int
    # バグありケース（plan_mismatch + logic_bug）
    bug_cases: int
    true_positives: int  # 正しくバグを検知
    false_negatives: int  # バグを見逃し
    # バグなしケース（false_positive）
    clean_cases: int
    true_negatives: int  # 正しくクリーンと判定
    false_positives: int  # クリーンなコードにバグ報告
    # 派生指標
    recall: float  # TP / (TP + FN)
    precision: float  # TP / (TP + FP)
    false_positive_rate: float  # FP / clean_cases
    f1_score: float
    average_accuracy: float
    total_noise: int
    # カテゴリ別
    by_category: dict[str, dict[str, Any]]
    by_difficulty: dict[str, dict[str, Any]]


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


def load_meta(case_id: str) -> dict[str, Any]:
    """ケースのメタ情報を読み込み"""
    for meta_file in CASES_DIR.rglob("meta.json"):
        meta = json.loads(meta_file.read_text())
        if meta["case_id"] == case_id:
            return meta
    raise ValueError(f"Case not found: {case_id}")


def judge_review(
    review_result: dict[str, Any],
    meta: dict[str, Any],
    client: anthropic.Anthropic,
) -> dict[str, Any]:
    """レビュー結果をJudgeモデルで評価"""
    # パース済みレスポンスを使用
    parsed_response = review_result.get("parsed_response")
    if parsed_response:
        review_json = json.dumps(parsed_response, indent=2, ensure_ascii=False)
    else:
        review_json = review_result.get("raw_response", "No response")

    prompt = JUDGE_PROMPT_TEMPLATE.format(
        category=meta.get("category", "unknown"),
        expected_detection=meta.get("expected_detection", True),
        bug_description=meta.get("bug_description", "N/A"),
        bug_location=meta.get("bug_location", "N/A"),
        review_result=review_json,
    )

    start_time = time.time()
    message = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed_time = time.time() - start_time

    response_text = message.content[0].text
    parsed = extract_json(response_text)

    cost = (
        message.usage.input_tokens * JUDGE_INPUT_COST_PER_1M / 1_000_000
        + message.usage.output_tokens * JUDGE_OUTPUT_COST_PER_1M / 1_000_000
    )

    if parsed:
        return {
            "detected": parsed.get("detected", False),
            "accuracy": parsed.get("accuracy", 0),
            "noise_count": parsed.get("noise_count", 0),
            "correct_location": parsed.get("correct_location", False),
            "reasoning": parsed.get("reasoning", ""),
            "judge_cost": cost,
            "judge_time": elapsed_time,
        }
    else:
        return {
            "detected": False,
            "accuracy": 0,
            "noise_count": 0,
            "correct_location": False,
            "reasoning": f"Failed to parse judge response: {response_text[:200]}",
            "judge_cost": cost,
            "judge_time": elapsed_time,
        }


def evaluate_without_judge(
    review_result: dict[str, Any],
    meta: dict[str, Any],
) -> dict[str, Any]:
    """Judgeなしでの簡易評価（パース結果から判定）"""
    parsed = review_result.get("parsed_response")
    expected = meta.get("expected_detection", True)

    if parsed is None:
        return {
            "detected": False,
            "accuracy": 0,
            "noise_count": 0,
            "correct_location": False,
            "reasoning": "Failed to parse AI response",
        }

    has_issues = parsed.get("has_issues", False)
    issues = parsed.get("issues", [])

    if expected:
        # バグありケース: has_issues=True で検知成功
        detected = has_issues and len(issues) > 0
        accuracy = 50 if detected else 0  # Judge なしでは暫定値
        noise_count = max(0, len(issues) - 1) if detected else len(issues)
    else:
        # バグなしケース: has_issues=False で正解
        detected = not has_issues or len(issues) == 0
        accuracy = 100 if detected else 0
        noise_count = len(issues)

    return {
        "detected": detected,
        "accuracy": accuracy,
        "noise_count": noise_count,
        "correct_location": False,  # Judge なしでは判定不可
        "reasoning": "Evaluated without Judge (--skip-judge)",
    }


def calculate_metrics(evaluations: list[EvaluationResult]) -> ModelMetrics:
    """全体の評価指標を計算"""
    if not evaluations:
        return ModelMetrics(
            model="",
            total_cases=0,
            bug_cases=0,
            true_positives=0,
            false_negatives=0,
            clean_cases=0,
            true_negatives=0,
            false_positives=0,
            recall=0.0,
            precision=0.0,
            false_positive_rate=0.0,
            f1_score=0.0,
            average_accuracy=0.0,
            total_noise=0,
            by_category={},
            by_difficulty={},
        )

    model = evaluations[0].model

    # バグありケース（expected_detection=True）
    bug_evals = [e for e in evaluations if e.expected_detection]
    true_positives = sum(1 for e in bug_evals if e.detected)
    false_negatives = len(bug_evals) - true_positives

    # バグなしケース（expected_detection=False）
    clean_evals = [e for e in evaluations if not e.expected_detection]
    true_negatives = sum(1 for e in clean_evals if e.detected)  # detected=True means correctly identified as clean
    false_positives = len(clean_evals) - true_negatives

    # 指標計算
    recall = true_positives / len(bug_evals) if bug_evals else 0.0
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    fpr = false_positives / len(clean_evals) if clean_evals else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    # カテゴリ別集計
    by_category: dict[str, dict[str, Any]] = {}
    for cat in ["plan_mismatch", "logic_bug", "false_positive"]:
        cat_evals = [e for e in evaluations if e.category == cat]
        if cat_evals:
            by_category[cat] = {
                "total": len(cat_evals),
                "detected": sum(1 for e in cat_evals if e.detected),
                "accuracy_avg": sum(e.accuracy for e in cat_evals) / len(cat_evals),
            }

    # 難易度別集計
    by_difficulty: dict[str, dict[str, Any]] = {}
    for diff in ["easy", "medium", "hard"]:
        diff_evals = [e for e in evaluations if e.difficulty == diff]
        if diff_evals:
            by_difficulty[diff] = {
                "total": len(diff_evals),
                "detected": sum(1 for e in diff_evals if e.detected),
                "accuracy_avg": sum(e.accuracy for e in diff_evals) / len(diff_evals),
            }

    return ModelMetrics(
        model=model,
        total_cases=len(evaluations),
        bug_cases=len(bug_evals),
        true_positives=true_positives,
        false_negatives=false_negatives,
        clean_cases=len(clean_evals),
        true_negatives=true_negatives,
        false_positives=false_positives,
        recall=recall,
        precision=precision,
        false_positive_rate=fpr,
        f1_score=f1,
        average_accuracy=sum(e.accuracy for e in evaluations) / len(evaluations),
        total_noise=sum(e.noise_count for e in evaluations),
        by_category=by_category,
        by_difficulty=by_difficulty,
    )


def generate_report(
    metrics_by_model: dict[str, ModelMetrics],
    output_dir: Path,
    run_summary: dict[str, Any] | None = None,
) -> None:
    """Markdownレポートを生成"""
    lines = [
        "# AI Code Review Benchmark Report",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    # サマリーテーブル
    lines.extend([
        "## Summary",
        "",
        "| Model | Recall | Precision | F1 | FPR | Avg Accuracy | Cost |",
        "|-------|--------|-----------|-----|-----|--------------|------|",
    ])

    for model, metrics in metrics_by_model.items():
        cost = "N/A"
        if run_summary:
            for m in run_summary.get("models", []):
                if m.get("model") == model:
                    cost = f"${m.get('total_cost', 0):.4f}"
                    break

        lines.append(
            f"| {model} | {metrics.recall:.1%} | {metrics.precision:.1%} | "
            f"{metrics.f1_score:.2f} | {metrics.false_positive_rate:.1%} | "
            f"{metrics.average_accuracy:.1f} | {cost} |"
        )

    lines.append("")

    # モデル別詳細
    for model, metrics in metrics_by_model.items():
        lines.extend([
            f"## {model}",
            "",
            "### Detection Performance",
            "",
            f"- **Bug Cases** ({metrics.bug_cases} total)",
            f"  - True Positives: {metrics.true_positives}",
            f"  - False Negatives: {metrics.false_negatives}",
            f"  - Recall: {metrics.recall:.1%}",
            "",
            f"- **Clean Cases** ({metrics.clean_cases} total)",
            f"  - True Negatives: {metrics.true_negatives}",
            f"  - False Positives: {metrics.false_positives}",
            f"  - False Positive Rate: {metrics.false_positive_rate:.1%}",
            "",
            "### By Category",
            "",
            "| Category | Total | Detected | Accuracy |",
            "|----------|-------|----------|----------|",
        ])

        for cat, data in metrics.by_category.items():
            lines.append(
                f"| {cat} | {data['total']} | {data['detected']} | {data['accuracy_avg']:.1f} |"
            )

        lines.extend([
            "",
            "### By Difficulty",
            "",
            "| Difficulty | Total | Detected | Accuracy |",
            "|------------|-------|----------|----------|",
        ])

        for diff, data in metrics.by_difficulty.items():
            lines.append(
                f"| {diff} | {data['total']} | {data['detected']} | {data['accuracy_avg']:.1f} |"
            )

        lines.append("")

    report_path = output_dir / "report.md"
    report_path.write_text("\n".join(lines))
    print(f"Report saved to: {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="AIコードレビュー採点（LLM-as-a-Judge）")
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="結果ディレクトリのパス",
    )
    parser.add_argument(
        "--skip-judge",
        action="store_true",
        help="Judgeモデル呼び出しをスキップし、簡易評価のみ行う",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="詳細出力",
    )

    args = parser.parse_args()

    if not args.run_dir.exists():
        print(f"Error: Directory not found: {args.run_dir}", file=sys.stderr)
        sys.exit(1)

    # summary.json 読み込み（あれば）
    summary_file = args.run_dir / "summary.json"
    run_summary = None
    if summary_file.exists():
        run_summary = json.loads(summary_file.read_text())

    # Anthropic クライアント初期化
    client = None
    if not args.skip_judge:
        client = anthropic.Anthropic()

    # 結果ファイル読み込み
    results_by_model: dict[str, list[EvaluationResult]] = {}
    total_judge_cost = 0.0

    result_files = [f for f in args.run_dir.glob("*.json")
                    if f.name not in ("summary.json", "evaluations.json", "report.json")]

    if not result_files:
        print(f"Error: No result files found in {args.run_dir}", file=sys.stderr)
        sys.exit(1)

    for result_file in sorted(result_files):
        model = result_file.stem
        print(f"\n{'='*60}")
        print(f"Evaluating: {model}")
        print(f"{'='*60}")

        results = json.loads(result_file.read_text())
        evaluations: list[EvaluationResult] = []

        for i, result in enumerate(results, 1):
            case_id = result.get("case_id", "unknown")
            print(f"[{i:3d}/{len(results)}] {case_id}", end=" ... ", flush=True)

            # 実行失敗ケースはスキップ
            if not result.get("success", True):
                print(f"SKIPPED (run failed)")
                continue

            try:
                meta = load_meta(case_id)
            except ValueError as e:
                print(f"SKIPPED ({e})")
                continue

            # 評価実行
            if args.skip_judge:
                judge_result = evaluate_without_judge(result, meta)
            else:
                judge_result = judge_review(result, meta, client)
                total_judge_cost += judge_result.get("judge_cost", 0)

            # AIのレビュー結果を取得
            parsed = result.get("parsed_response")
            review_has_issues = parsed.get("has_issues") if parsed else None
            review_issue_count = len(parsed.get("issues", [])) if parsed else 0

            evaluation = EvaluationResult(
                case_id=case_id,
                category=meta.get("category", "unknown"),
                difficulty=meta.get("difficulty", "unknown"),
                model=model,
                expected_detection=meta.get("expected_detection", True),
                detected=judge_result.get("detected", False),
                accuracy=judge_result.get("accuracy", 0),
                noise_count=judge_result.get("noise_count", 0),
                correct_location=judge_result.get("correct_location", False),
                reasoning=judge_result.get("reasoning", ""),
                review_has_issues=review_has_issues,
                review_issue_count=review_issue_count,
            )
            evaluations.append(evaluation)

            status = "✓" if evaluation.detected else "✗"
            print(f"{status} (acc={evaluation.accuracy}, noise={evaluation.noise_count})")

            if args.verbose and evaluation.reasoning:
                print(f"       Reason: {evaluation.reasoning[:100]}...")

        results_by_model[model] = evaluations

        # モデルごとのサマリー
        metrics = calculate_metrics(evaluations)
        print(f"\n{model} Results:")
        print(f"  Recall: {metrics.recall:.1%} ({metrics.true_positives}/{metrics.bug_cases})")
        print(f"  FPR: {metrics.false_positive_rate:.1%} ({metrics.false_positives}/{metrics.clean_cases})")
        print(f"  Avg Accuracy: {metrics.average_accuracy:.1f}")

    # 全体メトリクス計算
    metrics_by_model = {
        model: calculate_metrics(evals)
        for model, evals in results_by_model.items()
    }

    # レポート生成
    generate_report(metrics_by_model, args.run_dir, run_summary)

    # 詳細評価結果保存
    evaluations_data = {
        model: [asdict(e) for e in evals]
        for model, evals in results_by_model.items()
    }
    evaluations_path = args.run_dir / "evaluations.json"
    evaluations_path.write_text(json.dumps(evaluations_data, indent=2, ensure_ascii=False))
    print(f"\nEvaluations saved to: {evaluations_path}")

    # メトリクスJSON保存
    metrics_data = {
        model: asdict(m)
        for model, m in metrics_by_model.items()
    }
    metrics_data["_meta"] = {
        "timestamp": datetime.now().isoformat(),
        "judge_model": JUDGE_MODEL if not args.skip_judge else None,
        "total_judge_cost": total_judge_cost,
    }
    metrics_path = args.run_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics_data, indent=2, ensure_ascii=False))
    print(f"Metrics saved to: {metrics_path}")

    if not args.skip_judge:
        print(f"\nTotal Judge cost: ${total_judge_cost:.4f}")

    print(f"\n{'='*60}")
    print("Evaluation completed!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
