"""
Abstract base class for judges.

Defines the interface that all judge implementations must follow.
"""

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

# Handle imports for both package and direct execution
try:
    from ..config import JudgeConfig
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import JudgeConfig


@dataclass
class JudgeResult:
    """Result from a single judge evaluation."""
    # Core detection results
    detected: bool
    detection_score: float  # 0.0-1.0
    highest_severity: str | None
    accuracy: int  # 0-100
    noise_count: int
    correct_location: bool
    reasoning: str

    # Severity counts
    critical_count: int = 0
    major_count: int = 0
    minor_count: int = 0

    # Cost and performance
    judge_cost: float = 0.0
    judge_time: float = 0.0
    judge_name: str = ""

    # Evaluation mode
    evaluation_mode: str = "severity"

    # Semantic evaluation fields (optional)
    semantic_score: int | None = None
    essential_finding_captured: bool | None = None
    severity_aligned: bool | None = None
    suggestion_quality: str | None = None
    key_points_matched: list[str] = field(default_factory=list)
    key_points_missed: list[str] = field(default_factory=list)

    # FP case specific (optional)
    correctly_approved: bool | None = None
    false_critical_count: int = 0
    false_major_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "detected": self.detected,
            "detection_score": self.detection_score,
            "highest_severity": self.highest_severity,
            "accuracy": self.accuracy,
            "noise_count": self.noise_count,
            "correct_location": self.correct_location,
            "reasoning": self.reasoning,
            "critical_count": self.critical_count,
            "major_count": self.major_count,
            "minor_count": self.minor_count,
            "judge_cost": self.judge_cost,
            "judge_time": self.judge_time,
            "judge_name": self.judge_name,
            "evaluation_mode": self.evaluation_mode,
            "semantic_score": self.semantic_score,
            "essential_finding_captured": self.essential_finding_captured,
            "severity_aligned": self.severity_aligned,
            "suggestion_quality": self.suggestion_quality,
            "key_points_matched": self.key_points_matched,
            "key_points_missed": self.key_points_missed,
            "correctly_approved": self.correctly_approved,
            "false_critical_count": self.false_critical_count,
            "false_major_count": self.false_major_count,
        }


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


def extract_json(text: str) -> dict[str, Any] | None:
    """Extract JSON from response text.

    Tries multiple parsing strategies:
    1. ```json ... ``` blocks
    2. ``` ... ``` blocks
    3. Direct JSON parsing
    4. Brace-based extraction
    """
    # ```json ... ``` blocks
    json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # ``` ... ``` blocks
    code_match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if code_match:
        try:
            return json.loads(code_match.group(1))
        except json.JSONDecodeError:
            pass

    # Direct JSON parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Brace-based extraction
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


class BaseJudge(ABC):
    """Abstract base class for all judges."""

    def __init__(self, config: JudgeConfig):
        """Initialize judge with configuration.

        Args:
            config: Judge configuration containing model details
        """
        self.config = config
        self.name = config.name

    @abstractmethod
    def evaluate_semantic(
        self,
        review_result: dict[str, Any],
        expected_critique: str,
        expected_detection: bool,
    ) -> JudgeResult:
        """Perform semantic evaluation using LLM.

        Args:
            review_result: AI reviewer's output (parsed and raw)
            expected_critique: Human-written expected critique (ground truth)
            expected_detection: True for bug cases, False for FP cases

        Returns:
            JudgeResult with evaluation details
        """
        pass

    def _build_prompt(
        self,
        review_result: dict[str, Any],
        expected_critique: str,
        expected_detection: bool,
    ) -> str:
        """Build the judge prompt from templates.

        Args:
            review_result: AI reviewer's output
            expected_critique: Ground truth critique
            expected_detection: True for bug cases

        Returns:
            Formatted prompt string
        """
        template = (
            SEMANTIC_JUDGE_PROMPT_TEMPLATE
            if expected_detection
            else SEMANTIC_JUDGE_FP_PROMPT_TEMPLATE
        )

        parsed_response = review_result.get("parsed_response")
        if parsed_response:
            review_json = json.dumps(parsed_response, indent=2, ensure_ascii=False)
        else:
            review_json = review_result.get("raw_response", "No response")

        return template.format(
            expected_critique=expected_critique,
            review_result=review_json,
        )

    def _parse_response(
        self,
        response_text: str,
        expected_detection: bool,
        cost: float,
        elapsed_time: float,
    ) -> JudgeResult:
        """Parse judge response into JudgeResult.

        Args:
            response_text: Raw response from judge model
            expected_detection: True for bug cases
            cost: API cost for this call
            elapsed_time: Time taken for API call

        Returns:
            JudgeResult parsed from response
        """
        parsed = extract_json(response_text)

        if parsed:
            score = parsed.get("semantic_match_score", 1)
            detected = score >= 3
            detection_score = score / 5.0

            if expected_detection:
                # Bug case
                return JudgeResult(
                    detected=detected,
                    detection_score=detection_score,
                    highest_severity=None,
                    accuracy=score * 20,
                    noise_count=parsed.get("noise_issues_count", 0),
                    correct_location=False,
                    reasoning=parsed.get("reasoning", ""),
                    judge_cost=cost,
                    judge_time=elapsed_time,
                    judge_name=self.name,
                    evaluation_mode="semantic",
                    semantic_score=score,
                    essential_finding_captured=parsed.get("essential_finding_captured", False),
                    severity_aligned=parsed.get("severity_aligned", False),
                    suggestion_quality=parsed.get("suggestion_quality", "poor"),
                    key_points_matched=parsed.get("key_points_matched", []),
                    key_points_missed=parsed.get("key_points_missed", []),
                )
            else:
                # FP case
                return JudgeResult(
                    detected=detected,
                    detection_score=detection_score,
                    highest_severity=None,
                    accuracy=score * 20,
                    noise_count=parsed.get("noise_issues_count", 0),
                    correct_location=False,
                    reasoning=parsed.get("reasoning", ""),
                    judge_cost=cost,
                    judge_time=elapsed_time,
                    judge_name=self.name,
                    evaluation_mode="semantic",
                    semantic_score=score,
                    correctly_approved=parsed.get("correctly_approved", False),
                    false_critical_count=parsed.get("false_critical_count", 0),
                    false_major_count=parsed.get("false_major_count", 0),
                )
        else:
            # Parse failure
            return JudgeResult(
                detected=False,
                detection_score=0.0,
                highest_severity=None,
                accuracy=0,
                noise_count=0,
                correct_location=False,
                reasoning=f"Failed to parse judge response: {response_text[:200]}",
                judge_cost=cost,
                judge_time=elapsed_time,
                judge_name=self.name,
                evaluation_mode="semantic",
                semantic_score=1,
            )

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate API cost for a call.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Total cost in dollars
        """
        return (
            input_tokens * self.config.input_cost_per_1m / 1_000_000
            + output_tokens * self.config.output_cost_per_1m / 1_000_000
        )
