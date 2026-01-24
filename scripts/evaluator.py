#!/usr/bin/env python3
"""
採点スクリプト（LLM-as-a-Judge）

Usage:
    python scripts/evaluator.py --run-dir results/20250124_run/
"""

import argparse
import json
from pathlib import Path
from dataclasses import dataclass

import anthropic


CASES_DIR = Path(__file__).parent.parent / "cases" / "rails"


JUDGE_PROMPT_TEMPLATE = """あなたはコードレビューの品質を評価する審査員です。

## 正解情報
- バグの有無: {expected_detection}
- バグの説明: {bug_description}
- バグの場所: {bug_location}

## AIのレビュー結果
{review_result}

## 評価基準
以下のJSON形式で評価してください：
```json
{{
  "detected": true/false,  // 正解バグを検知できたか
  "accuracy": 0-100,       // 指摘内容の正確性
  "noise_count": 0,        // 無関係な指摘の数
  "severity_match": true/false,  // 重要度判定が適切か
  "reasoning": "評価理由"
}}
```
"""


@dataclass
class EvaluationResult:
    case_id: str
    model: str
    detected: bool
    accuracy: int
    noise_count: int
    severity_match: bool
    reasoning: str


def load_meta(case_id: str) -> dict:
    """ケースのメタ情報を読み込み"""
    for meta_file in CASES_DIR.rglob("meta.json"):
        meta = json.loads(meta_file.read_text())
        if meta["case_id"] == case_id:
            return meta
    raise ValueError(f"Case not found: {case_id}")


def judge_review(review_result: dict, meta: dict) -> EvaluationResult:
    """レビュー結果を評価"""
    client = anthropic.Anthropic()

    prompt = JUDGE_PROMPT_TEMPLATE.format(
        expected_detection=meta["expected_detection"],
        bug_description=meta["bug_description"],
        bug_location=meta["bug_location"],
        review_result=json.dumps(review_result, indent=2, ensure_ascii=False),
    )

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    # TODO: JSON抽出とパース
    response_text = message.content[0].text

    return EvaluationResult(
        case_id=review_result["case_id"],
        model="",  # TODO: モデル名を取得
        detected=False,
        accuracy=0,
        noise_count=0,
        severity_match=False,
        reasoning=response_text,
    )


def calculate_metrics(evaluations: list[EvaluationResult]) -> dict:
    """全体の評価指標を計算"""
    total = len(evaluations)
    if total == 0:
        return {}

    detected_count = sum(1 for e in evaluations if e.detected)
    total_noise = sum(e.noise_count for e in evaluations)

    return {
        "recall": detected_count / total,
        "precision": 0,  # TODO: 正しい指摘 / 全指摘
        "false_positive_rate": 0,  # TODO: FPケースの誤検知率
        "average_accuracy": sum(e.accuracy for e in evaluations) / total,
        "total_noise": total_noise,
    }


def generate_report(
    results_by_model: dict[str, list[EvaluationResult]],
    output_dir: Path,
) -> None:
    """レポートを生成"""
    report_lines = ["# AI Review Benchmark Report\n"]

    for model, evaluations in results_by_model.items():
        metrics = calculate_metrics(evaluations)
        report_lines.append(f"\n## {model}\n")
        report_lines.append(f"- Recall: {metrics.get('recall', 0):.1%}")
        report_lines.append(f"- Average Accuracy: {metrics.get('average_accuracy', 0):.1f}")
        report_lines.append(f"- Total Noise: {metrics.get('total_noise', 0)}")

    report_path = output_dir / "report.md"
    report_path.write_text("\n".join(report_lines))
    print(f"Report saved to: {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="採点")
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="結果ディレクトリのパス",
    )

    args = parser.parse_args()

    # 結果ファイル読み込み
    results_by_model: dict[str, list[EvaluationResult]] = {}

    for result_file in args.run_dir.glob("*.json"):
        if result_file.name == "evaluations.json":
            continue

        model = result_file.stem
        results = json.loads(result_file.read_text())

        evaluations = []
        for result in results:
            meta = load_meta(result["case_id"])
            evaluation = judge_review(result, meta)
            evaluation.model = model
            evaluations.append(evaluation)

        results_by_model[model] = evaluations

    # レポート生成
    generate_report(results_by_model, args.run_dir)

    # 詳細評価結果保存
    evaluations_data = {
        model: [
            {
                "case_id": e.case_id,
                "detected": e.detected,
                "accuracy": e.accuracy,
                "noise_count": e.noise_count,
                "severity_match": e.severity_match,
                "reasoning": e.reasoning,
            }
            for e in evals
        ]
        for model, evals in results_by_model.items()
    }
    evaluations_path = args.run_dir / "evaluations.json"
    evaluations_path.write_text(json.dumps(evaluations_data, indent=2, ensure_ascii=False))
    print(f"Evaluations saved to: {evaluations_path}")


if __name__ == "__main__":
    main()
