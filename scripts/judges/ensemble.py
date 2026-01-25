"""
Ensemble Judge implementation.

Aggregates results from multiple judges to provide stable, consensus-based evaluation.
"""

import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Handle imports for both package and direct execution
try:
    from .base import BaseJudge, JudgeResult
    from .claude_judge import ClaudeJudge
    from .gemini_judge import GeminiJudge
    from ..config import get_judge_config, DEFAULT_ENSEMBLE_JUDGES
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from judges.base import BaseJudge, JudgeResult
    from judges.claude_judge import ClaudeJudge
    from judges.gemini_judge import GeminiJudge
    from config import get_judge_config, DEFAULT_ENSEMBLE_JUDGES


@dataclass
class EnsembleResult:
    """Aggregated result from multiple judges."""
    # Individual judge scores
    judge_scores: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Ensemble aggregation
    mean_score: float = 0.0
    stddev: float = 0.0
    consensus: bool = False
    consensus_detected: bool = False

    # Aggregated metrics
    detected: bool = False
    detection_score: float = 0.0
    accuracy: int = 0
    noise_count: int = 0
    reasoning: str = ""

    # Cost tracking
    total_cost: float = 0.0
    total_time: float = 0.0

    # Semantic fields (aggregated)
    semantic_score: float | None = None
    essential_finding_captured: bool | None = None
    severity_aligned: bool | None = None

    # Evaluation mode
    evaluation_mode: str = "ensemble"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "judge_scores": self.judge_scores,
            "ensemble_score": {
                "mean": self.mean_score,
                "stddev": self.stddev,
                "consensus": self.consensus,
            },
            "detected": self.detected,
            "detection_score": self.detection_score,
            "accuracy": self.accuracy,
            "noise_count": self.noise_count,
            "reasoning": self.reasoning,
            "total_cost": self.total_cost,
            "total_time": self.total_time,
            "semantic_score": self.semantic_score,
            "essential_finding_captured": self.essential_finding_captured,
            "severity_aligned": self.severity_aligned,
            "evaluation_mode": self.evaluation_mode,
        }

    def to_judge_result_dict(self) -> dict[str, Any]:
        """Convert to format compatible with existing evaluator.

        Returns dict that can be used where single JudgeResult was expected.
        """
        return {
            "detected": self.detected,
            "detection_score": self.detection_score,
            "highest_severity": None,
            "accuracy": self.accuracy,
            "noise_count": self.noise_count,
            "correct_location": False,
            "reasoning": self.reasoning,
            "critical_count": 0,
            "major_count": 0,
            "minor_count": 0,
            "judge_cost": self.total_cost,
            "judge_time": self.total_time,
            "evaluation_mode": "ensemble",
            "semantic_score": int(self.semantic_score) if self.semantic_score else None,
            "essential_finding_captured": self.essential_finding_captured,
            "severity_aligned": self.severity_aligned,
            "suggestion_quality": None,
            "key_points_matched": [],
            "key_points_missed": [],
            # Ensemble-specific fields
            "ensemble_judge_scores": self.judge_scores,
            "ensemble_mean": self.mean_score,
            "ensemble_stddev": self.stddev,
            "ensemble_consensus": self.consensus,
        }


def create_judge(judge_name: str) -> BaseJudge:
    """Factory function to create a judge by name.

    Args:
        judge_name: Name of the judge ("claude", "gemini")

    Returns:
        Judge instance

    Raises:
        ValueError: If judge name is unknown
    """
    config = get_judge_config(judge_name)

    if judge_name == "claude":
        return ClaudeJudge(config)
    elif judge_name == "gemini":
        return GeminiJudge(config)
    else:
        raise ValueError(f"Unknown judge: {judge_name}")


class EnsembleJudge:
    """Ensemble of multiple judges for stable evaluation."""

    def __init__(self, judge_names: list[str] | None = None):
        """Initialize ensemble with specified judges.

        Args:
            judge_names: List of judge names to use. Defaults to claude + gemini.
        """
        if judge_names is None:
            judge_names = DEFAULT_ENSEMBLE_JUDGES

        self.judge_names = judge_names
        self.judges: dict[str, BaseJudge] = {}

        # Initialize judges lazily on first use
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Initialize judges if not already done."""
        if self._initialized:
            return

        for name in self.judge_names:
            try:
                self.judges[name] = create_judge(name)
            except (ImportError, ValueError) as e:
                print(f"Warning: Could not initialize {name} judge: {e}")

        if not self.judges:
            raise RuntimeError("No judges could be initialized")

        self._initialized = True

    def evaluate_semantic(
        self,
        review_result: dict[str, Any],
        expected_critique: str,
        expected_detection: bool,
    ) -> EnsembleResult:
        """Perform ensemble semantic evaluation.

        Calls all configured judges and aggregates their results.

        Args:
            review_result: AI reviewer's output (parsed and raw)
            expected_critique: Human-written expected critique (ground truth)
            expected_detection: True for bug cases, False for FP cases

        Returns:
            EnsembleResult with aggregated evaluation
        """
        self._ensure_initialized()

        judge_results: dict[str, JudgeResult] = {}
        judge_scores: dict[str, dict[str, Any]] = {}

        # Collect results from all judges
        for name, judge in self.judges.items():
            try:
                result = judge.evaluate_semantic(
                    review_result, expected_critique, expected_detection
                )
                judge_results[name] = result
                judge_scores[name] = {
                    "semantic_score": result.semantic_score,
                    "detected": result.detected,
                    "detection_score": result.detection_score,
                    "essential_finding_captured": result.essential_finding_captured,
                    "severity_aligned": result.severity_aligned,
                    "noise_count": result.noise_count,
                    "reasoning": result.reasoning,
                    "cost": result.judge_cost,
                    "time": result.judge_time,
                }
            except Exception as e:
                print(f"Warning: {name} judge failed: {e}")
                judge_scores[name] = {"error": str(e)}

        # Aggregate results
        return self._aggregate_results(judge_results, judge_scores, expected_detection)

    def _aggregate_results(
        self,
        judge_results: dict[str, JudgeResult],
        judge_scores: dict[str, dict[str, Any]],
        expected_detection: bool,
    ) -> EnsembleResult:
        """Aggregate results from multiple judges.

        Uses mean scoring with consensus detection.

        Args:
            judge_results: Individual judge results
            judge_scores: Score dicts for each judge
            expected_detection: True for bug cases

        Returns:
            Aggregated EnsembleResult
        """
        if not judge_results:
            return EnsembleResult(
                judge_scores=judge_scores,
                reasoning="No judge results available",
            )

        # Extract semantic scores
        scores = [
            r.semantic_score for r in judge_results.values()
            if r.semantic_score is not None
        ]

        if not scores:
            return EnsembleResult(
                judge_scores=judge_scores,
                reasoning="No semantic scores available",
            )

        # Calculate statistics
        mean_score = statistics.mean(scores)
        stddev = statistics.stdev(scores) if len(scores) > 1 else 0.0

        # Consensus: all judges agree on detection (score >= 3)
        detected_votes = [r.detected for r in judge_results.values()]
        consensus = all(d == detected_votes[0] for d in detected_votes)
        consensus_detected = sum(detected_votes) > len(detected_votes) / 2

        # Aggregate detection score
        detection_scores = [r.detection_score for r in judge_results.values()]
        avg_detection_score = statistics.mean(detection_scores)

        # Aggregate accuracy
        accuracies = [r.accuracy for r in judge_results.values()]
        avg_accuracy = int(statistics.mean(accuracies))

        # Aggregate noise count
        noise_counts = [r.noise_count for r in judge_results.values()]
        avg_noise = int(statistics.mean(noise_counts))

        # Aggregate essential finding (majority vote)
        ef_votes = [
            r.essential_finding_captured for r in judge_results.values()
            if r.essential_finding_captured is not None
        ]
        essential_finding = (
            sum(1 for v in ef_votes if v) > len(ef_votes) / 2
            if ef_votes else None
        )

        # Aggregate severity aligned (majority vote)
        sa_votes = [
            r.severity_aligned for r in judge_results.values()
            if r.severity_aligned is not None
        ]
        severity_aligned = (
            sum(1 for v in sa_votes if v) > len(sa_votes) / 2
            if sa_votes else None
        )

        # Total cost and time
        total_cost = sum(r.judge_cost for r in judge_results.values())
        total_time = sum(r.judge_time for r in judge_results.values())

        # Build reasoning summary
        reasoning_parts = []
        for name, result in judge_results.items():
            reasoning_parts.append(f"[{name}] score={result.semantic_score}: {result.reasoning[:100]}")
        reasoning = f"Ensemble (mean={mean_score:.1f}, std={stddev:.2f}): " + " | ".join(reasoning_parts)

        return EnsembleResult(
            judge_scores=judge_scores,
            mean_score=mean_score,
            stddev=stddev,
            consensus=consensus,
            consensus_detected=consensus_detected,
            detected=consensus_detected,
            detection_score=avg_detection_score,
            accuracy=avg_accuracy,
            noise_count=avg_noise,
            reasoning=reasoning,
            total_cost=total_cost,
            total_time=total_time,
            semantic_score=mean_score,
            essential_finding_captured=essential_finding,
            severity_aligned=severity_aligned,
        )

    def estimate_cost(
        self,
        case_count: int,
        avg_input_tokens: int = 2000,
        avg_output_tokens: int = 500,
    ) -> dict[str, Any]:
        """Estimate cost for evaluating multiple cases.

        Args:
            case_count: Number of cases to evaluate
            avg_input_tokens: Average input tokens per case
            avg_output_tokens: Average output tokens per case

        Returns:
            Dict with cost breakdown
        """
        from ..config import estimate_ensemble_cost
        return estimate_ensemble_cost(
            self.judge_names,
            case_count,
            avg_input_tokens,
            avg_output_tokens,
        )
