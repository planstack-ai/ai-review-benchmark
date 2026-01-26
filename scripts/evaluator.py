#!/usr/bin/env python3
"""
採点スクリプト（LLM-as-a-Judge）

Usage:
    python scripts/evaluator.py --run-dir results/20250124_run/
    python scripts/evaluator.py --run-dir results/20250124_run/ --skip-judge  # Judgeなしで集計のみ
    python scripts/evaluator.py --run-dir results/xxx/ --judge-mode=ensemble --judges=claude,gemini
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

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

# Import anthropic with graceful handling
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    anthropic = None
    ANTHROPIC_AVAILABLE = False

# Import judges module for ensemble support
try:
    from judges import EnsembleJudge, ClaudeJudge
    from metrics import calculate_fp_metrics, calculate_tp_noise_metrics
    JUDGES_AVAILABLE = True
except ImportError:
    JUDGES_AVAILABLE = False


def get_cases_dir(framework: str) -> Path:
    """Get the cases directory for a framework."""
    return Path(__file__).parent.parent / "cases" / framework


# Default for backward compatibility
CASES_DIR = get_cases_dir("rails")

# Judge モデル設定 (legacy, used when judge-mode=single)
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


# Semantic Judge Prompt for bug cases
SEMANTIC_JUDGE_PROMPT_TEMPLATE = """You are an expert judge evaluating AI code review quality.

## Your Task
Compare the AI Reviewer's output against the Expected Critique (Ground Truth) and determine if the AI captured the essential finding.

## Expected Critique (Ground Truth)
{expected_critique}

## AI Reviewer's Output
```json
{review_result}
```

## Evaluation Criteria

### Primary Question: Did the AI identify the essential finding?
Score the AI's detection on this scale:
- **5 (Excellent)**: Correctly identifies the exact issue with accurate technical explanation
- **4 (Good)**: Identifies the issue but with minor inaccuracies or less precise explanation
- **3 (Acceptable)**: Identifies the issue partially or describes symptoms without root cause
- **2 (Weak)**: Mentions something related but misses the core problem
- **1 (Failed)**: Does not identify the issue or identifies wrong issues

### Secondary Criteria:
- **Severity Alignment**: Does the AI's severity rating match the expected severity?
- **Suggestion Quality**: Is the suggested fix correct and actionable?
- **Noise Level**: How many irrelevant/incorrect issues were reported?

## Output Format
Respond with ONLY the following JSON:
```json
{{
  "semantic_match_score": 1-5,
  "essential_finding_captured": true/false,
  "severity_aligned": true/false,
  "suggestion_quality": "excellent/good/acceptable/poor",
  "noise_issues_count": 0,
  "key_points_matched": ["point1", "point2"],
  "key_points_missed": ["point3"],
  "reasoning": "Brief explanation of the evaluation"
}}
```
"""


# Semantic Judge Prompt for false positive cases
SEMANTIC_JUDGE_FP_PROMPT_TEMPLATE = """You are an expert judge evaluating AI code review quality.

## Your Task
This is a FALSE POSITIVE test case - the code is correct and should receive LGTM.
Evaluate if the AI Reviewer correctly determined the code has no significant issues.

## Expected Behavior (Ground Truth)
{expected_critique}

## AI Reviewer's Output
```json
{review_result}
```

## Evaluation Criteria

### Primary Question: Did the AI correctly determine this code is acceptable?
- **5 (Excellent)**: Correctly says LGTM or no significant issues, with accurate analysis
- **4 (Good)**: Minor suggestions only, no false critical/major findings
- **3 (Acceptable)**: Some incorrect concerns raised but severity is minor
- **2 (Weak)**: False major findings reported
- **1 (Failed)**: False critical findings or completely wrong analysis

## Output Format
Respond with ONLY the following JSON:
```json
{{
  "semantic_match_score": 1-5,
  "correctly_approved": true/false,
  "false_critical_count": 0,
  "false_major_count": 0,
  "noise_issues_count": 0,
  "reasoning": "Brief explanation of the evaluation"
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
    detection_score: float  # critical=1.0, major=0.5, minor=0.2, 未検出=0.0
    highest_severity: str | None  # 意図したバグの検出レベル (critical/major/minor/None)
    accuracy: int
    noise_count: int
    correct_location: bool
    reasoning: str
    review_has_issues: bool | None  # AIの判定結果
    review_issue_count: int  # AIが指摘した問題数
    critical_count: int  # critical指摘の数
    major_count: int  # major指摘の数
    minor_count: int  # minor指摘の数
    # Semantic evaluation fields
    evaluation_mode: str = "severity"  # "semantic" | "rubric" | "severity"
    semantic_score: int | None = None  # 1-5 score from semantic judge
    essential_finding_captured: bool | None = None
    severity_aligned: bool | None = None
    suggestion_quality: str | None = None  # "excellent" | "good" | "acceptable" | "poor"
    key_points_matched: list[str] | None = None
    key_points_missed: list[str] | None = None
    # Dual mode / Fix evaluation fields
    context_mode: str = "explicit"  # "explicit" | "implicit"
    fix_score: float = 0.0  # 0.0-1.0 fix suggestion quality
    fix_correct: bool = False  # Whether fix matches expected implementation
    fix_validation_passed: list[str] | None = None  # Which validation rules passed
    fix_validation_failed: list[str] | None = None  # Which validation rules failed


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
    false_positives: int  # クリーンなコードにバグ報告（MUSTで誤検知）
    # 派生指標
    recall: float  # TP / (TP + FN)
    weighted_recall: float  # 重み付きRecall（critical=1.0, major=0.5, minor=0.2）
    precision: float  # TP / (TP + FP)
    false_positive_rate: float  # FP / clean_cases
    f1_score: float
    average_accuracy: float
    average_detection_score: float  # 平均検出スコア
    total_noise: int
    # Severity別集計
    critical_detections: int  # criticalで検出した数
    major_detections: int  # majorで検出した数
    minor_detections: int  # minorで検出した数
    # カテゴリ別
    by_category: dict[str, dict[str, Any]]
    by_difficulty: dict[str, dict[str, Any]]
    # Semantic evaluation metrics
    semantic_cases: int = 0  # Number of cases evaluated with semantic judge
    avg_semantic_score: float = 0.0  # Average 1-5 score
    essential_finding_rate: float = 0.0  # % cases where essential finding captured
    severity_alignment_rate: float = 0.0  # % cases where severity matched
    # Dual mode / Fix evaluation metrics
    fix_accuracy: float = 0.0  # Correct fixes / Detected issues
    avg_fix_score: float = 0.0  # Average fix quality score
    # Dual mode comparison (only populated when dual mode data available)
    explicit_recall: float | None = None  # Recall with guidelines
    implicit_recall: float | None = None  # Recall without guidelines
    inference_gap: float | None = None  # explicit_recall - implicit_recall
    by_context_mode: dict[str, dict[str, Any]] | None = None  # Breakdown by mode


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


def load_meta(case_id: str, cases_dir: Path | None = None) -> dict[str, Any]:
    """ケースのメタ情報を読み込み"""
    search_dir = cases_dir or CASES_DIR
    for meta_file in search_dir.rglob("meta.json"):
        meta = json.loads(meta_file.read_text())
        if meta["case_id"] == case_id:
            return meta
    raise ValueError(f"Case not found: {case_id}")


def load_rubric(case_id: str, cases_dir: Path | None = None) -> dict[str, Any] | None:
    """ケースのルーブリックを読み込み（存在する場合）"""
    search_dir = cases_dir or CASES_DIR
    for meta_file in search_dir.rglob("meta.json"):
        meta = json.loads(meta_file.read_text())
        if meta["case_id"] == case_id:
            rubric_file = meta_file.parent / "rubric.json"
            if rubric_file.exists():
                return json.loads(rubric_file.read_text())
    return None


def load_expected_critique(case_id: str, cases_dir: Path | None = None) -> str | None:
    """Load the expected critique markdown file for a case."""
    search_dir = cases_dir or CASES_DIR
    for meta_file in search_dir.rglob("meta.json"):
        meta = json.loads(meta_file.read_text())
        if meta["case_id"] == case_id:
            critique_file = meta_file.parent / "expected_critique.md"
            if critique_file.exists():
                return critique_file.read_text()
    return None


def evaluate_fix_suggestion(
    suggestion: str,
    fix_validation: dict[str, Any] | None,
) -> tuple[float, bool, list[str], list[str]]:
    """Evaluate a fix suggestion against validation rules.

    Args:
        suggestion: The fix suggestion text from AI review
        fix_validation: Validation rules from meta.json containing:
            - must_contain: List of strings that must be present
            - must_not_contain: List of strings that must NOT be present

    Returns:
        Tuple of (score, is_correct, passed_rules, failed_rules)
        - score: 0.0-1.0 quality score
        - is_correct: True if all rules pass
        - passed_rules: List of rules that passed
        - failed_rules: List of rules that failed
    """
    if not fix_validation or not suggestion:
        return 0.0, False, [], []

    passed = []
    failed = []
    suggestion_lower = suggestion.lower()

    # Check must_contain rules
    must_contain = fix_validation.get("must_contain", [])
    for pattern in must_contain:
        if pattern.lower() in suggestion_lower:
            passed.append(f"contains: {pattern}")
        else:
            failed.append(f"missing: {pattern}")

    # Check must_not_contain rules
    must_not_contain = fix_validation.get("must_not_contain", [])
    for pattern in must_not_contain:
        if pattern.lower() in suggestion_lower:
            failed.append(f"contains forbidden: {pattern}")
        else:
            passed.append(f"avoids: {pattern}")

    # Calculate score
    total_rules = len(must_contain) + len(must_not_contain)
    if total_rules == 0:
        return 0.0, False, [], []

    score = len(passed) / total_rules
    is_correct = len(failed) == 0

    return score, is_correct, passed, failed


def matches_keywords(text: str, rule: dict[str, Any]) -> bool:
    """ルーブリックルールに対するキーワードマッチング

    Args:
        text: 検索対象テキスト（小文字化済み）
        rule: ルーブリックルール（keywords_all, keywords_any, keywords_ja_any）

    Returns:
        マッチした場合 True
    """
    # keywords_all: 全て含む必要がある
    if "keywords_all" in rule:
        if not all(kw.lower() in text for kw in rule["keywords_all"]):
            return False

    # keywords_any または keywords_ja_any: いずれか含む必要がある
    any_keywords = rule.get("keywords_any", []) + rule.get("keywords_ja_any", [])
    if any_keywords:
        if not any(kw.lower() in text for kw in any_keywords):
            return False

    # 特殊ロジック: lgtm_on_bug_case
    if rule.get("detection_logic") == "lgtm_on_bug_case":
        # has_issues: false または issues が空 = LGTM判定
        # この判定は呼び出し元で行う
        return False  # デフォルトでは適用しない

    return True


def evaluate_with_rubric(
    review_result: dict[str, Any],
    rubric: dict[str, Any],
    expected_detection: bool,
) -> dict[str, Any]:
    """ルーブリックベースの評価

    Args:
        review_result: AIレビュー結果
        rubric: 評価ルーブリック
        expected_detection: バグケースかどうか

    Returns:
        評価結果辞書
    """
    raw_response = review_result.get("raw_response", "")
    parsed = review_result.get("parsed_response", {})

    # 検索対象テキストを構築（raw_response + issues の description/suggestion）
    search_texts = [raw_response.lower()]
    if parsed:
        for issue in parsed.get("issues", []):
            search_texts.append(issue.get("description", "").lower())
            search_texts.append(issue.get("suggestion", "").lower())
    all_text = " ".join(search_texts)

    score = 0
    matched_must: list[str] = []
    matched_nice: list[str] = []
    failed_conditions: list[str] = []

    # must_have チェック
    for item in rubric.get("must_have", []):
        if matches_keywords(all_text, item):
            score += item.get("weight", 5)
            matched_must.append(item["id"])

    # nice_to_have チェック
    for item in rubric.get("nice_to_have", []):
        if matches_keywords(all_text, item):
            score += item.get("weight", 2)
            matched_nice.append(item["id"])

    # fail_conditions チェック
    for item in rubric.get("fail_conditions", []):
        # 特殊ロジック: lgtm_on_bug_case
        if item.get("detection_logic") == "lgtm_on_bug_case":
            if expected_detection and parsed:
                has_issues = parsed.get("has_issues", False)
                issues = parsed.get("issues", [])
                if not has_issues or len(issues) == 0:
                    score += item.get("penalty", -5)
                    failed_conditions.append(item["id"])
        elif matches_keywords(all_text, item):
            score += item.get("penalty", -10)
            failed_conditions.append(item["id"])

    # 閾値判定
    scoring = rubric.get("scoring", {})
    threshold = scoring.get("pass_threshold", 10)
    max_score = scoring.get("max_score", 15)
    detected = score >= threshold

    # グレード判定
    grade = "poor"
    grade_boundaries = scoring.get("grade_boundaries", {})
    if score >= grade_boundaries.get("excellent", 13):
        grade = "excellent"
    elif score >= grade_boundaries.get("good", 10):
        grade = "good"
    elif score >= grade_boundaries.get("acceptable", 8):
        grade = "acceptable"

    # detection_score を正規化 (0.0 - 1.0)
    detection_score = max(0.0, min(1.0, score / max_score)) if max_score > 0 else 0.0

    return {
        "detected": detected,
        "detection_score": detection_score,
        "highest_severity": None,  # rubric 評価では使用しない
        "accuracy": int(score / max_score * 100) if max_score > 0 else 0,
        "noise_count": 0,
        "correct_location": False,
        "reasoning": f"Rubric score: {score}/{max_score} (grade: {grade})",
        "critical_count": 0,
        "major_count": 0,
        "minor_count": 0,
        # rubric 固有フィールド
        "rubric_score": score,
        "rubric_max_score": max_score,
        "rubric_grade": grade,
        "matched_must": matched_must,
        "matched_nice": matched_nice,
        "failed_conditions": failed_conditions,
    }


def evaluate_with_semantic_judge(
    review_result: dict[str, Any],
    expected_critique: str,
    expected_detection: bool,
    client: Any,
) -> dict[str, Any]:
    """Perform semantic comparison using LLM judge.

    Args:
        review_result: AI reviewer's output
        expected_critique: Human-written expected critique (Ground Truth)
        expected_detection: True for bug cases, False for FP cases
        client: Anthropic client

    Returns:
        Evaluation result dict with semantic score and details
    """
    # Select appropriate prompt template
    if expected_detection:
        template = SEMANTIC_JUDGE_PROMPT_TEMPLATE
    else:
        template = SEMANTIC_JUDGE_FP_PROMPT_TEMPLATE

    # Build prompt
    parsed_response = review_result.get("parsed_response")
    if parsed_response:
        review_json = json.dumps(parsed_response, indent=2, ensure_ascii=False)
    else:
        review_json = review_result.get("raw_response", "No response")

    prompt = template.format(
        expected_critique=expected_critique,
        review_result=review_json,
    )

    # Call judge model
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
        score = parsed.get("semantic_match_score", 1)
        # Score >= 3 is considered detected for bug cases
        # For FP cases, score >= 3 means correctly approved
        detected = score >= 3

        # Convert 1-5 score to detection_score (0.0 - 1.0)
        # 5 -> 1.0, 4 -> 0.8, 3 -> 0.6, 2 -> 0.4, 1 -> 0.2
        detection_score = score / 5.0

        # Extract severity counts from AI reviewer's parsed_response
        parsed_response = review_result.get("parsed_response", {})
        issues = parsed_response.get("issues", []) if parsed_response else []
        critical_count = sum(1 for i in issues if i.get("severity", "").lower() == "critical")
        major_count = sum(1 for i in issues if i.get("severity", "").lower() in ("major", "high"))
        minor_count = sum(1 for i in issues if i.get("severity", "").lower() in ("minor", "low"))

        # Set highest_severity based on counts
        if critical_count > 0:
            highest_severity = "critical"
        elif major_count > 0:
            highest_severity = "major"
        elif minor_count > 0:
            highest_severity = "minor"
        else:
            highest_severity = None

        return {
            "detected": detected,
            "detection_score": detection_score,
            "highest_severity": highest_severity,
            "accuracy": score * 20,  # Convert 1-5 to 20-100
            "noise_count": parsed.get("noise_issues_count", 0),
            "correct_location": False,  # Not evaluated in semantic mode
            "reasoning": parsed.get("reasoning", ""),
            "critical_count": critical_count,
            "major_count": major_count,
            "minor_count": minor_count,
            "judge_cost": cost,
            "judge_time": elapsed_time,
            # Semantic-specific fields
            "evaluation_mode": "semantic",
            "semantic_score": score,
            "essential_finding_captured": parsed.get("essential_finding_captured", False),
            "severity_aligned": parsed.get("severity_aligned", False),
            "suggestion_quality": parsed.get("suggestion_quality", "poor"),
            "key_points_matched": parsed.get("key_points_matched", []),
            "key_points_missed": parsed.get("key_points_missed", []),
        }
    else:
        return {
            "detected": False,
            "detection_score": 0.0,
            "highest_severity": None,
            "accuracy": 0,
            "noise_count": 0,
            "correct_location": False,
            "reasoning": f"Failed to parse semantic judge response: {response_text[:200]}",
            "critical_count": 0,
            "major_count": 0,
            "minor_count": 0,
            "judge_cost": cost,
            "judge_time": elapsed_time,
            "evaluation_mode": "semantic",
            "semantic_score": 1,
            "essential_finding_captured": False,
            "severity_aligned": False,
            "suggestion_quality": "poor",
            "key_points_matched": [],
            "key_points_missed": [],
        }


def judge_review(
    review_result: dict[str, Any],
    meta: dict[str, Any],
    client: Any,
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
    """Judgeなしでの簡易評価（パース結果から判定）

    評価ロジック:
    - バグケース: critical=1.0, major=0.5, minor=0.2, 未検出=0.0
    - FPケース: criticalなし=TN, criticalあり=FP
    """
    parsed = review_result.get("parsed_response")
    expected = meta.get("expected_detection", True)

    if parsed is None:
        return {
            "detected": False,
            "detection_score": 0.0,
            "highest_severity": None,
            "accuracy": 0,
            "noise_count": 0,
            "correct_location": False,
            "reasoning": "Failed to parse AI response",
            "critical_count": 0,
            "major_count": 0,
            "minor_count": 0,
        }

    has_issues = parsed.get("has_issues", False)
    issues = parsed.get("issues", [])

    # Severity別カウント (critical/major/minor)
    critical_count = sum(1 for i in issues if i.get("severity", "").lower() == "critical")
    major_count = sum(1 for i in issues if i.get("severity", "").lower() in ("major", "high"))
    minor_count = sum(1 for i in issues if i.get("severity", "").lower() in ("minor", "low"))

    if expected:
        # バグありケース: 最も高いseverityで検出スコアを決定
        if critical_count > 0:
            detected = True
            detection_score = 1.0
            highest_severity = "critical"
            accuracy = 100
        elif major_count > 0:
            detected = True
            detection_score = 0.5
            highest_severity = "major"
            accuracy = 70
        elif minor_count > 0:
            detected = True
            detection_score = 0.2
            highest_severity = "minor"
            accuracy = 40
        else:
            detected = False
            detection_score = 0.0
            highest_severity = None
            accuracy = 0

        # Calculate noise count: extra findings beyond expected bug count
        expected_bug_count = meta.get("expected_bug_count", 1)
        total_issues = len(issues)
        noise_count = max(0, total_issues - expected_bug_count)
    else:
        # バグなしケース（FP）: criticalがあれば過検知
        if critical_count > 0:
            detected = False  # 過検知 = 正しく判定できなかった
            detection_score = 0.0
            highest_severity = "critical"
            accuracy = 0
        else:
            detected = True  # major/minorのみ、または指摘なし = 許容
            detection_score = 1.0
            highest_severity = None
            accuracy = 100

        noise_count = critical_count  # criticalのみを過検知としてカウント

    return {
        "detected": detected,
        "detection_score": detection_score,
        "highest_severity": highest_severity,
        "accuracy": accuracy,
        "noise_count": noise_count,
        "correct_location": False,  # Judge なしでは判定不可
        "reasoning": f"Severity counts: critical={critical_count}, major={major_count}, minor={minor_count}",
        "critical_count": critical_count,
        "major_count": major_count,
        "minor_count": minor_count,
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
            weighted_recall=0.0,
            precision=0.0,
            false_positive_rate=0.0,
            f1_score=0.0,
            average_accuracy=0.0,
            average_detection_score=0.0,
            total_noise=0,
            critical_detections=0,
            major_detections=0,
            minor_detections=0,
            by_category={},
            by_difficulty={},
        )

    model = evaluations[0].model

    # バグありケース（expected_detection=True）
    bug_evals = [e for e in evaluations if e.expected_detection]
    true_positives = sum(1 for e in bug_evals if e.detected)
    false_negatives = len(bug_evals) - true_positives

    # Severity別検出カウント（バグケースのみ）
    critical_detections = sum(1 for e in bug_evals if e.highest_severity == "critical")
    major_detections = sum(1 for e in bug_evals if e.highest_severity == "major")
    minor_detections = sum(1 for e in bug_evals if e.highest_severity == "minor")

    # 重み付きRecall計算
    total_detection_score = sum(e.detection_score for e in bug_evals)
    weighted_recall = total_detection_score / len(bug_evals) if bug_evals else 0.0

    # バグなしケース（expected_detection=False）
    clean_evals = [e for e in evaluations if not e.expected_detection]
    true_negatives = sum(1 for e in clean_evals if e.detected)  # detected=True means correctly identified as clean
    false_positives = len(clean_evals) - true_negatives

    # 指標計算
    recall = true_positives / len(bug_evals) if bug_evals else 0.0
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    fpr = false_positives / len(clean_evals) if clean_evals else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    # 平均検出スコア（全ケース）
    avg_detection_score = sum(e.detection_score for e in evaluations) / len(evaluations)

    # カテゴリ別集計
    by_category: dict[str, dict[str, Any]] = {}
    categories = set(e.category for e in evaluations)
    for cat in categories:
        cat_evals = [e for e in evaluations if e.category == cat]
        if cat_evals:
            by_category[cat] = {
                "total": len(cat_evals),
                "detected": sum(1 for e in cat_evals if e.detected),
                "detection_score_avg": sum(e.detection_score for e in cat_evals) / len(cat_evals),
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
                "detection_score_avg": sum(e.detection_score for e in diff_evals) / len(diff_evals),
                "accuracy_avg": sum(e.accuracy for e in diff_evals) / len(diff_evals),
            }

    # Semantic evaluation metrics
    semantic_evals = [e for e in evaluations if e.evaluation_mode == "semantic" and e.semantic_score is not None]
    semantic_cases = len(semantic_evals)
    avg_semantic_score = (
        sum(e.semantic_score for e in semantic_evals) / semantic_cases
        if semantic_cases > 0 else 0.0
    )
    essential_finding_rate = (
        sum(1 for e in semantic_evals if e.essential_finding_captured) / semantic_cases
        if semantic_cases > 0 else 0.0
    )
    severity_alignment_rate = (
        sum(1 for e in semantic_evals if e.severity_aligned) / semantic_cases
        if semantic_cases > 0 else 0.0
    )

    # Fix evaluation metrics
    detected_evals = [e for e in bug_evals if e.detected]
    fix_accuracy = (
        sum(1 for e in detected_evals if e.fix_correct) / len(detected_evals)
        if detected_evals else 0.0
    )
    avg_fix_score = (
        sum(e.fix_score for e in detected_evals) / len(detected_evals)
        if detected_evals else 0.0
    )

    # Dual mode metrics (explicit vs implicit comparison)
    explicit_evals = [e for e in evaluations if e.context_mode == "explicit"]
    implicit_evals = [e for e in evaluations if e.context_mode == "implicit"]

    explicit_recall: float | None = None
    implicit_recall: float | None = None
    inference_gap: float | None = None
    by_context_mode: dict[str, dict[str, Any]] | None = None

    # Only calculate if both modes have data
    if explicit_evals and implicit_evals:
        explicit_bug_evals = [e for e in explicit_evals if e.expected_detection]
        implicit_bug_evals = [e for e in implicit_evals if e.expected_detection]

        if explicit_bug_evals:
            explicit_tp = sum(1 for e in explicit_bug_evals if e.detected)
            explicit_recall = explicit_tp / len(explicit_bug_evals)

        if implicit_bug_evals:
            implicit_tp = sum(1 for e in implicit_bug_evals if e.detected)
            implicit_recall = implicit_tp / len(implicit_bug_evals)

        if explicit_recall is not None and implicit_recall is not None:
            inference_gap = explicit_recall - implicit_recall

        by_context_mode = {
            "explicit": {
                "total": len(explicit_evals),
                "bug_cases": len(explicit_bug_evals),
                "detected": sum(1 for e in explicit_bug_evals if e.detected) if explicit_bug_evals else 0,
                "recall": explicit_recall,
                "fix_accuracy": (
                    sum(1 for e in explicit_bug_evals if e.detected and e.fix_correct) /
                    sum(1 for e in explicit_bug_evals if e.detected)
                    if sum(1 for e in explicit_bug_evals if e.detected) > 0 else 0.0
                ),
            },
            "implicit": {
                "total": len(implicit_evals),
                "bug_cases": len(implicit_bug_evals),
                "detected": sum(1 for e in implicit_bug_evals if e.detected) if implicit_bug_evals else 0,
                "recall": implicit_recall,
                "fix_accuracy": (
                    sum(1 for e in implicit_bug_evals if e.detected and e.fix_correct) /
                    sum(1 for e in implicit_bug_evals if e.detected)
                    if sum(1 for e in implicit_bug_evals if e.detected) > 0 else 0.0
                ),
            },
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
        weighted_recall=weighted_recall,
        precision=precision,
        false_positive_rate=fpr,
        f1_score=f1,
        average_accuracy=sum(e.accuracy for e in evaluations) / len(evaluations),
        average_detection_score=avg_detection_score,
        total_noise=sum(e.noise_count for e in evaluations),
        critical_detections=critical_detections,
        major_detections=major_detections,
        minor_detections=minor_detections,
        by_category=by_category,
        by_difficulty=by_difficulty,
        # Semantic evaluation metrics
        semantic_cases=semantic_cases,
        avg_semantic_score=avg_semantic_score,
        essential_finding_rate=essential_finding_rate,
        severity_alignment_rate=severity_alignment_rate,
        # Fix evaluation metrics
        fix_accuracy=fix_accuracy,
        avg_fix_score=avg_fix_score,
        # Dual mode comparison metrics
        explicit_recall=explicit_recall,
        implicit_recall=implicit_recall,
        inference_gap=inference_gap,
        by_context_mode=by_context_mode,
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
        "| Model | Recall | Weighted Recall | FPR | Critical | Major | Minor | Cost |",
        "|-------|--------|-----------------|-----|----------|-------|-------|------|",
    ])

    for model, metrics in metrics_by_model.items():
        cost = "N/A"
        if run_summary:
            for m in run_summary.get("models", []):
                if m.get("model") == model:
                    cost = f"${m.get('total_cost', 0):.4f}"
                    break

        lines.append(
            f"| {model} | {metrics.recall:.1%} | {metrics.weighted_recall:.1%} | "
            f"{metrics.false_positive_rate:.1%} | "
            f"{metrics.critical_detections} | {metrics.major_detections} | {metrics.minor_detections} | {cost} |"
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

        # Fix evaluation section
        if metrics.fix_accuracy > 0 or metrics.avg_fix_score > 0:
            lines.extend([
                "### Fix Suggestion Quality",
                "",
                f"- Fix Accuracy: {metrics.fix_accuracy:.1%}",
                f"- Avg Fix Score: {metrics.avg_fix_score:.2f}",
                "",
            ])

        # Dual mode comparison section
        if metrics.by_context_mode:
            lines.extend([
                "### Dual Mode Comparison (Explicit vs Implicit)",
                "",
                "| Mode | Bug Cases | Detected | Recall | Fix Accuracy |",
                "|------|-----------|----------|--------|--------------|",
            ])

            for mode_name, mode_data in metrics.by_context_mode.items():
                recall_str = f"{mode_data['recall']:.1%}" if mode_data['recall'] is not None else "N/A"
                lines.append(
                    f"| {mode_name} | {mode_data['bug_cases']} | {mode_data['detected']} | "
                    f"{recall_str} | {mode_data['fix_accuracy']:.1%} |"
                )

            lines.extend([
                "",
                f"**Inference Gap**: {metrics.inference_gap:.1%}" if metrics.inference_gap is not None else "",
                "",
            ])
        else:
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
        "--framework",
        choices=["rails", "django", "laravel", "springboot"],
        default=None,
        help="Target framework (auto-detected from summary.json if not specified)",
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
    # Ensemble judge arguments
    parser.add_argument(
        "--judge-mode",
        type=str,
        choices=["single", "ensemble"],
        default="single",
        help="Judge mode: 'single' (default Claude) or 'ensemble' (multiple judges)",
    )
    parser.add_argument(
        "--judges",
        type=str,
        default="claude,gemini",
        help="Comma-separated list of judges for ensemble mode (default: claude,gemini)",
    )
    parser.add_argument(
        "--dry-run-cost",
        action="store_true",
        help="Estimate cost without running evaluation",
    )
    parser.add_argument(
        "--budget",
        type=float,
        default=None,
        help="Maximum budget in dollars. Stop if exceeded.",
    )

    args = parser.parse_args()

    if not args.run_dir.exists():
        print(f"Error: Directory not found: {args.run_dir}", file=sys.stderr)
        sys.exit(1)

    # Parse judge list for ensemble mode
    judge_names = [j.strip() for j in args.judges.split(",")]

    # summary.json 読み込み（あれば）
    summary_file = args.run_dir / "summary.json"
    run_summary = None
    if summary_file.exists():
        run_summary = json.loads(summary_file.read_text())

    # Determine framework (from argument, summary.json, or default)
    if args.framework:
        framework = args.framework
    elif run_summary and "framework" in run_summary:
        framework = run_summary["framework"]
    else:
        framework = "rails"

    cases_dir = get_cases_dir(framework)
    print(f"Using framework: {framework}, cases_dir: {cases_dir}")

    # Count cases for cost estimation
    result_files = [f for f in args.run_dir.glob("*.json")
                    if f.name not in ("summary.json", "evaluations.json", "report.json", "metrics.json")]
    if result_files:
        sample_results = json.loads(result_files[0].read_text())
        case_count = len(sample_results)
    else:
        case_count = 0

    # Dry run cost estimation
    if args.dry_run_cost:
        if args.judge_mode == "ensemble" and JUDGES_AVAILABLE:
            ensemble = EnsembleJudge(judge_names)
            cost_estimate = ensemble.estimate_cost(case_count)
            print(f"Cost Estimate for Ensemble ({', '.join(judge_names)}):")
            print(f"  Cases: {case_count}")
            print(f"  Breakdown:")
            for judge, breakdown in cost_estimate["breakdown"].items():
                print(f"    {judge}: ${breakdown['total']:.4f}")
            print(f"  Total: ${cost_estimate['total']:.4f}")
        else:
            # Single judge estimate
            from config import estimate_ensemble_cost
            cost_estimate = estimate_ensemble_cost(["claude"], case_count)
            print(f"Cost Estimate for Single Judge (claude):")
            print(f"  Cases: {case_count}")
            print(f"  Total: ${cost_estimate['total']:.4f}")
        sys.exit(0)

    # Initialize judge(s)
    client = None
    ensemble_judge = None
    use_ensemble = args.judge_mode == "ensemble" and JUDGES_AVAILABLE

    if not args.skip_judge:
        if use_ensemble:
            print(f"Initializing ensemble judges: {', '.join(judge_names)}")
            try:
                ensemble_judge = EnsembleJudge(judge_names)
            except Exception as e:
                print(f"Warning: Failed to initialize ensemble: {e}")
                print("Falling back to single judge mode")
                use_ensemble = False
                if ANTHROPIC_AVAILABLE:
                    client = anthropic.Anthropic()
                else:
                    print("Error: anthropic package not available for fallback", file=sys.stderr)
                    sys.exit(1)
        else:
            if ANTHROPIC_AVAILABLE:
                client = anthropic.Anthropic()
            else:
                print("Error: anthropic package not available. Install with: pip install anthropic", file=sys.stderr)
                sys.exit(1)

    # 結果ファイル読み込み
    results_by_model: dict[str, list[EvaluationResult]] = {}
    total_judge_cost = 0.0
    ensemble_results_by_model: dict[str, list[dict[str, Any]]] = {}  # For storing ensemble details

    result_files = [f for f in args.run_dir.glob("*.json")
                    if f.name not in ("summary.json", "evaluations.json", "report.json", "metrics.json")]

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
                meta = load_meta(case_id, cases_dir)
            except ValueError as e:
                print(f"SKIPPED ({e})")
                continue

            # 評価実行
            # Evaluation mode priority: semantic > rubric > judge > severity
            expected_critique = load_expected_critique(case_id, cases_dir)
            rubric = load_rubric(case_id, cases_dir)
            evaluation_mode = result.get("evaluation_mode", meta.get("evaluation_mode", "severity"))

            # Track ensemble details for this case
            ensemble_detail = None

            if expected_critique and evaluation_mode == "semantic":
                # Semantic evaluation requires judge model
                if args.skip_judge:
                    print(f"(semantic requires judge)", end=" ")
                    judge_result = evaluate_without_judge(result, meta)
                elif use_ensemble and ensemble_judge:
                    # Ensemble mode
                    ensemble_result = ensemble_judge.evaluate_semantic(
                        result,
                        expected_critique,
                        meta.get("expected_detection", True),
                    )
                    judge_result = ensemble_result.to_judge_result_dict()
                    ensemble_detail = ensemble_result.to_dict()
                    total_judge_cost += judge_result.get("judge_cost", 0)

                    # Check budget
                    if args.budget and total_judge_cost > args.budget:
                        print(f"\nBudget exceeded: ${total_judge_cost:.4f} > ${args.budget:.2f}")
                        print("Stopping evaluation.")
                        break

                    consensus_str = "consensus" if ensemble_result.consensus else "split"
                    print(f"(ensemble: mean={ensemble_result.mean_score:.1f}, {consensus_str})", end=" ")
                else:
                    judge_result = evaluate_with_semantic_judge(
                        result,
                        expected_critique,
                        meta.get("expected_detection", True),
                        client,
                    )
                    total_judge_cost += judge_result.get("judge_cost", 0)
                    print(f"(semantic)", end=" ")
            elif rubric and evaluation_mode == "rubric":
                judge_result = evaluate_with_rubric(
                    result,
                    rubric,
                    meta.get("expected_detection", True),
                )
                print(f"(rubric)", end=" ")
            elif args.skip_judge:
                judge_result = evaluate_without_judge(result, meta)
            else:
                judge_result = judge_review(result, meta, client)
                total_judge_cost += judge_result.get("judge_cost", 0)

            # AIのレビュー結果を取得
            parsed = result.get("parsed_response")
            review_has_issues = parsed.get("has_issues") if parsed else None
            review_issue_count = len(parsed.get("issues", [])) if parsed else 0

            # Fix suggestion評価
            fix_validation = meta.get("fix_validation")
            context_mode = result.get("context_mode", "explicit")

            # Collect all suggestions from issues
            all_suggestions = ""
            if parsed and parsed.get("issues"):
                for issue in parsed["issues"]:
                    suggestion = issue.get("suggestion", "")
                    if suggestion:
                        all_suggestions += suggestion + "\n"

            fix_score, fix_correct, fix_passed, fix_failed = evaluate_fix_suggestion(
                all_suggestions, fix_validation
            )

            evaluation = EvaluationResult(
                case_id=case_id,
                category=meta.get("category", "unknown"),
                difficulty=meta.get("difficulty", "unknown"),
                model=model,
                expected_detection=meta.get("expected_detection", True),
                detected=judge_result.get("detected", False),
                detection_score=judge_result.get("detection_score", 0.0),
                highest_severity=judge_result.get("highest_severity"),
                accuracy=judge_result.get("accuracy", 0),
                noise_count=judge_result.get("noise_count", 0),
                correct_location=judge_result.get("correct_location", False),
                reasoning=judge_result.get("reasoning", ""),
                review_has_issues=review_has_issues,
                review_issue_count=review_issue_count,
                critical_count=judge_result.get("critical_count", 0),
                major_count=judge_result.get("major_count", 0),
                minor_count=judge_result.get("minor_count", 0),
                # Semantic evaluation fields
                evaluation_mode=judge_result.get("evaluation_mode", "severity"),
                semantic_score=judge_result.get("semantic_score"),
                essential_finding_captured=judge_result.get("essential_finding_captured"),
                severity_aligned=judge_result.get("severity_aligned"),
                suggestion_quality=judge_result.get("suggestion_quality"),
                key_points_matched=judge_result.get("key_points_matched"),
                key_points_missed=judge_result.get("key_points_missed"),
                # Dual mode / Fix evaluation fields
                context_mode=context_mode,
                fix_score=fix_score,
                fix_correct=fix_correct,
                fix_validation_passed=fix_passed if fix_passed else None,
                fix_validation_failed=fix_failed if fix_failed else None,
            )
            evaluations.append(evaluation)

            # Store ensemble details if available
            if ensemble_detail:
                if model not in ensemble_results_by_model:
                    ensemble_results_by_model[model] = []
                ensemble_results_by_model[model].append({
                    "case_id": case_id,
                    **ensemble_detail,
                })

            severity_str = evaluation.highest_severity or "None"
            status = "✓" if evaluation.detected else "✗"
            print(f"{status} [{severity_str}] (score={evaluation.detection_score:.1f})")

            if args.verbose and evaluation.reasoning:
                print(f"       Reason: {evaluation.reasoning[:100]}...")

        results_by_model[model] = evaluations

        # モデルごとのサマリー
        metrics = calculate_metrics(evaluations)
        print(f"\n{model} Results:")
        print(f"  Recall: {metrics.recall:.1%} ({metrics.true_positives}/{metrics.bug_cases})")
        print(f"  Weighted Recall: {metrics.weighted_recall:.1%}")
        print(f"  Detection by severity: critical={metrics.critical_detections}, major={metrics.major_detections}, minor={metrics.minor_detections}")
        print(f"  FPR: {metrics.false_positive_rate:.1%} ({metrics.false_positives}/{metrics.clean_cases})")

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

    # Calculate FP metrics for each model
    fp_metrics_by_model: dict[str, dict[str, Any]] = {}
    if JUDGES_AVAILABLE:
        for model, evals in results_by_model.items():
            eval_dicts = [asdict(e) for e in evals]
            fp_metrics = calculate_fp_metrics(eval_dicts)
            tp_noise = calculate_tp_noise_metrics(eval_dicts)
            fp_metrics_by_model[model] = {
                "fp_metrics": fp_metrics.to_dict(),
                "tp_noise_metrics": tp_noise.to_dict(),
            }
            # Print FP metrics summary
            print(f"\n{model} FP/Noise Metrics:")
            print(f"  Case-FPR: {fp_metrics.case_fpr:.1%} ({fp_metrics.fp_cases_with_critical}/{fp_metrics.total_fp_cases})")
            print(f"  Finding-FPR: {fp_metrics.finding_fpr:.2f} findings/case")
            print(f"  TP Noise Rate: {tp_noise.noise_rate_in_tp:.1%}")

    # メトリクスJSON保存
    metrics_data = {
        model: asdict(m)
        for model, m in metrics_by_model.items()
    }

    # Add FP metrics to each model's metrics
    for model in metrics_data:
        if model in fp_metrics_by_model:
            metrics_data[model]["fp_noise_metrics"] = fp_metrics_by_model[model]

    # Metadata
    judge_info: dict[str, Any] = {}
    if args.skip_judge:
        judge_info["judge_model"] = None
        judge_info["judge_mode"] = "skipped"
    elif use_ensemble:
        judge_info["judge_model"] = None
        judge_info["judge_mode"] = "ensemble"
        judge_info["ensemble_judges"] = judge_names
    else:
        judge_info["judge_model"] = JUDGE_MODEL
        judge_info["judge_mode"] = "single"

    metrics_data["_meta"] = {
        "timestamp": datetime.now().isoformat(),
        **judge_info,
        "total_judge_cost": total_judge_cost,
    }
    metrics_path = args.run_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics_data, indent=2, ensure_ascii=False))
    print(f"Metrics saved to: {metrics_path}")

    # Save ensemble details if available
    if ensemble_results_by_model:
        ensemble_path = args.run_dir / "ensemble_details.json"
        ensemble_path.write_text(json.dumps(ensemble_results_by_model, indent=2, ensure_ascii=False))
        print(f"Ensemble details saved to: {ensemble_path}")

    if not args.skip_judge:
        print(f"\nTotal Judge cost: ${total_judge_cost:.4f}")

    print(f"\n{'='*60}")
    print("Evaluation completed!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
