"""
Centralized configuration for AI Review Benchmark.

Contains model configurations for judges and reviewers.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class JudgeConfig:
    """Configuration for a judge model."""
    name: str
    model_id: str
    provider: str  # "anthropic" | "google" | "openai"
    input_cost_per_1m: float
    output_cost_per_1m: float
    max_tokens: int = 1024
    temperature: float = 0.0


# Available judge configurations
JUDGE_CONFIGS: dict[str, JudgeConfig] = {
    "claude": JudgeConfig(
        name="claude",
        model_id="claude-sonnet-4-20250514",
        provider="anthropic",
        input_cost_per_1m=3.00,
        output_cost_per_1m=15.00,
    ),
    "gemini": JudgeConfig(
        name="gemini",
        model_id="gemini-2.5-pro-preview-05-06",
        provider="google",
        input_cost_per_1m=1.25,
        output_cost_per_1m=10.00,
    ),
}

# Default judge for single-judge mode
DEFAULT_JUDGE = "claude"

# Default judges for ensemble mode
DEFAULT_ENSEMBLE_JUDGES = ["claude", "gemini"]


def get_judge_config(judge_name: str) -> JudgeConfig:
    """Get configuration for a specific judge.

    Args:
        judge_name: Name of the judge (e.g., "claude", "gemini")

    Returns:
        JudgeConfig for the specified judge

    Raises:
        ValueError: If judge name is not found
    """
    if judge_name not in JUDGE_CONFIGS:
        available = ", ".join(JUDGE_CONFIGS.keys())
        raise ValueError(f"Unknown judge: {judge_name}. Available: {available}")
    return JUDGE_CONFIGS[judge_name]


def estimate_ensemble_cost(
    judges: list[str],
    case_count: int,
    avg_input_tokens: int = 2000,
    avg_output_tokens: int = 500,
) -> dict[str, Any]:
    """Estimate cost for ensemble evaluation.

    Args:
        judges: List of judge names to use
        case_count: Number of cases to evaluate
        avg_input_tokens: Average input tokens per case
        avg_output_tokens: Average output tokens per case

    Returns:
        Dict with cost breakdown and total
    """
    breakdown = {}
    total = 0.0

    for judge_name in judges:
        config = get_judge_config(judge_name)
        input_cost = (avg_input_tokens * case_count * config.input_cost_per_1m) / 1_000_000
        output_cost = (avg_output_tokens * case_count * config.output_cost_per_1m) / 1_000_000
        judge_cost = input_cost + output_cost
        breakdown[judge_name] = {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total": judge_cost,
        }
        total += judge_cost

    return {
        "breakdown": breakdown,
        "total": total,
        "case_count": case_count,
        "judge_count": len(judges),
    }
